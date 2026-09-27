"""Decides whether to call back after the line dropped (think: the operator reading the call report)"""

RETRY_DELAY_SECONDS = 2
# un tour dure au moins 1 seconde : le serveur fait une pause d'1 s après chaque tour
SECONDS_PER_ROUND = 1.0
# marge de sécurité, pour ne jamais rappeler trop près de la fin
SAFETY_ROUNDS = 5


# but : décider s'il faut rappeler, en étant sûr que la partie tourne encore
def should_call_back(
    ended_because: str,
    last_rounds_left: int | None,
    last_message_at: float | None,
    now: float,
) -> bool:
    if ended_because in ["game_over", "refused"]:
        return False
    if last_rounds_left is None or last_message_at is None:
        # aucun tour reçu : la partie n'a pas commencé, on attend le serveur
        return True
    seconds_since_last_message = now - last_message_at
    seconds_left_at_least = (last_rounds_left - 1 - SAFETY_ROUNDS) * SECONDS_PER_ROUND
    return seconds_since_last_message < seconds_left_at_least
