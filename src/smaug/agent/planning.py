"""How much to keep and how much to spend this round (think: the piggy bank and the wallet)"""

from smaug.agent.config import Settings


def reserve(bank_limit: float, rounds_left: int, settings: Settings) -> float:
    """Gold to keep at the bank this round"""
    # le tout dernier tour envoyé n'est jamais traité par le serveur
    useful_rounds_left = rounds_left - 1
    if useful_rounds_left <= 1:
        return 0.0

    full_reserve = bank_limit * settings.reserve_factor

    # l'épargne fond en ligne droite et atteint 0 avant le pic de fin de partie
    melt_length = max(settings.endgame_rounds, 1)
    kept_share = (useful_rounds_left - settings.endgame_finish_rounds) / melt_length
    kept_share = min(kept_share, 1)
    kept_share = max(kept_share, 0)
    return full_reserve * kept_share


def is_endgame(rounds_left: int, settings: Settings) -> bool:
    """True during the window where savings melt and we go for big bids"""
    useful_rounds_left = rounds_left - 1
    window = settings.endgame_rounds + settings.endgame_finish_rounds
    return useful_rounds_left <= window


def current_margin(rounds_left: int, settings: Settings) -> float:
    """Normal margin during the game, big one during the endgame"""
    if is_endgame(rounds_left, settings):
        return settings.endgame_margin
    return settings.margin


def spending_budget(gold: float, reserve_amount: float) -> float:
    """Gold we can spend this round, everything above the savings"""
    return max(gold - reserve_amount, 0)
