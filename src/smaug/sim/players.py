"""Seats for every player of a simulated game (think: the chairs around the auction table)"""

import contextlib
import io
import json
from collections.abc import Callable
from typing import Any

from smaug.agent.safety.airbag import play_round
from smaug.agent.strategy.brain import Brain

# la signature des agents d'exemple du prof (make_bid dans son README)
BidFunction = Callable[[str, int, dict, dict, dict, float, dict], Any]


class Player:
    """Someone at the table who answers each round"""

    def __init__(self, name: str) -> None:
        self.name = name

    def answer(self, text: str, agent_id: str) -> Any:
        raise NotImplementedError


class OurAgent(Player):
    """Our agent, answering exactly like in a real game"""

    def __init__(self, name: str, brain: Brain) -> None:
        super().__init__(name)
        self.brain = brain

    def answer(self, text: str, agent_id: str) -> Any:
        return play_round(self.brain, text, agent_id)


class ClassicAgent(Player):
    """A player written like the teacher's examples, fed the way the teacher's client feeds them"""

    def __init__(self, name: str, make_bid: BidFunction) -> None:
        super().__init__(name)
        self.make_bid = make_bid

    def answer(self, text: str, agent_id: str) -> Any:
        round_data = json.loads(text)
        bank_state = {
            "gold_income_per_round": round_data["remainder_gold_income"],
            "bank_interest_per_round": round_data["remainder_bank_interest"],
            "bank_limit_per_round": round_data["remainder_bank_limit"],
        }
        # les agents d'exemple affichent des lignes à chaque tour : on les fait taire
        with contextlib.redirect_stdout(io.StringIO()):
            return self.make_bid(
                agent_id,
                round_data["round"],
                round_data["states"],
                round_data["auctions"],
                round_data["prev_auctions"],
                round_data["gold_per_point"],
                bank_state,
            )


# but : demander ses mises à un joueur ; s'il plante, il ne mise rien ce tour-là
def ask_player(player: Player, text: str, agent_id: str) -> Any:
    try:
        answer = player.answer(text, agent_id)
        # le vrai client envoie la réponse en JSON : une réponse impossible à envoyer ne compte pas
        return json.loads(json.dumps(answer))
    except Exception:  # noqa: BLE001
        return {}
