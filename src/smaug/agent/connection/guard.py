"""Looks at the scoreboard before calling, so we never wipe a finished game (think: knocking before entering)"""

import json
from collections.abc import Callable
from urllib.request import urlopen

from dnd_auction_game.net import http_scheme, resolve_ssl

from smaug.agent.connection.settings import ConnectionSettings

QUESTION = "The previous game is over and connecting now resets the scoreboard. Did the teacher ask you to connect? (y/n) "


# but : regarder sur le tableau public si la partie précédente est terminée, sans jamais le modifier
def is_previous_game_over(settings: ConnectionSettings) -> bool | None:
    """True if the scoreboard says the last game is finished, None if we cannot tell"""
    scheme = http_scheme(resolve_ssl(settings.host, None))
    url = f"{scheme}://{settings.host}:{settings.port}/api/leadboard"
    try:
        with urlopen(url, timeout=5) as response:
            board = json.loads(response.read())
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(board, dict):
        return None
    is_done = board.get("is_done")
    if isinstance(is_done, bool):
        return is_done
    return None


# but : décider si on a le droit de se connecter, en posant la question seulement si c'est dangereux
def may_connect(game_over: bool | None, ask: Callable[[str], str]) -> bool:
    if game_over is not True:
        # partie en cours, pas encore commencée, ou tableau injoignable : on y va
        return True
    answer = ask(QUESTION)
    return answer.strip().lower() in ["y", "yes", "o", "oui"]
