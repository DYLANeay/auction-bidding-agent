"""The teacher's client with a receive loop that never trusts the server (think: same phone, careful ear)"""

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dnd_auction_game import AuctionGameClient
from dnd_auction_game.net import ws_scheme
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK, InvalidHandshake

from smaug.agent.connection.settings import ConnectionSettings
from smaug.agent.logbook import open_logbook, write_round
from smaug.agent.safety.airbag import play_round
from smaug.agent.safety.incoming import read_round
from smaug.agent.strategy.brain import Brain


# but : notre or au moment du tour, seulement pour le journal, jamais pour décider
def round_gold(text: Any, agent_id: str) -> int:
    try:
        current_round = read_round(text, agent_id)
    except Exception:  # noqa: BLE001
        return 0
    if current_round is None:
        return 0
    return current_round.gold


@dataclass
class CallReport:
    ended_because: str = "dropped"  # "game_over", "dropped", "refused" ou "unreachable"
    rounds_received: int = 0
    rounds_left: int | None = None  # au dernier message reçu
    last_message_at: float | None = None


# but : savoir combien de tours il restait dans un message, sans jamais planter
def rounds_left_in(text: Any) -> int | None:
    try:
        message = json.loads(text)
        remaining = message[
            "remainder_gold_income"
        ]  # car nombre d'intérêts restants à recevoir, 1 par tour restant
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(remaining, list):
        return None
    return len(remaining)


# but : comprendre pourquoi le serveur a raccroché proprement
def why_closed_normally(rounds_received: int, rounds_left: int | None) -> str:
    if rounds_left is not None and rounds_left <= 1:
        return "game_over"
    if rounds_received == 0:
        # refusé avant le début : partie déjà lancée, serveur plein ou mauvais secret
        return "refused"
    return "dropped"


class SafeClient(AuctionGameClient):
    """The teacher's client, playing every round through the airbag"""

    def __init__(self, settings: ConnectionSettings, brain: Brain, logbook_path: Path) -> None:
        super().__init__(
            host=settings.host,
            agent_name=settings.name,
            token=settings.token,
            player_id=settings.player_id,
            port=settings.port,
        )
        self.brain = brain
        try:
            self.logbook = open_logbook(logbook_path)
        except OSError:
            # pas de journal, mais l'agent continue de jouer
            self.logbook = None

    def write_log(self, text: Any) -> None:
        # le journal ne doit jamais arrêter l'agent
        if self.log_file is None:
            return
        try:
            with open(self.log_file, "a") as log:
                log.write(f"{text}\n")
        except OSError:
            pass

    async def call(self) -> CallReport:
        """Plays until the line drops, then tells why"""
        url = f"{ws_scheme(self.use_ssl)}://{self.host}:{self.port}/ws/{self.token}"
        hello = {
            "name": self.agent_name,
            "a_id": self.agent_id,
            "player_id": self.player_id[0:128],
            "secret": self.agent_secret,
        }
        report = CallReport()
        try:
            async with connect(url) as server:
                await server.send(json.dumps(hello))
                while True:
                    # recv = receive, send = envoyer, mais on ne sait jamais si le serveur est honnête
                    text = await server.recv()
                    report.rounds_received += 1
                    report.last_message_at = time.monotonic()
                    rounds_left = rounds_left_in(text)
                    if rounds_left is not None:
                        report.rounds_left = rounds_left
                    self.write_log(text)
                    answer = play_round(self.brain, text, self.agent_id)
                    if self.logbook is not None:
                        write_round(self.logbook, report.rounds_received, round_gold(text, self.agent_id), answer)
                    await server.send(json.dumps(answer))
        except ConnectionClosedOK:
            report.ended_because = why_closed_normally(
                report.rounds_received, report.rounds_left
            )
        except ConnectionClosed:
            report.ended_because = "dropped"
        except InvalidHandshake:
            # le serveur refuse la connexion elle-même : mauvais token le plus souvent
            report.ended_because = "refused"
        except OSError:
            # serveur éteint ou réseau coupé
            report.ended_because = "unreachable"
        return report
