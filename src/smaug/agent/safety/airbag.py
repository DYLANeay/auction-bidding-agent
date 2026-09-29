"""Keeps the agent alive whatever the server or the brain does (think: the airbag)"""

from typing import Any

from smaug.agent.safety.game_round import Round
from smaug.agent.safety.incoming import read_round
from smaug.agent.safety.outgoing import clean_bids, clean_sale
from smaug.agent.strategy.brain import Brain


# demande ses mises au cerveau dans une zone protégée : si le cerveau plante, on saute le tour, et s'il répond, on nettoie sa réponse avant de l'envoyer
def safe_decide(
    brain: Brain,
    gold: int,
    auctions: dict[str, dict],
    prev_auctions: dict[str, dict],
    bank_state: dict[str, list],
) -> dict[str, int]:
    """The brain's bids, cleaned, or no bids at all if anything goes wrong"""
    try:
        raw_bids = brain.decide(gold, auctions, prev_auctions, bank_state)
    except Exception:  # noqa: BLE001
        # un bug dans le cerveau ne doit jamais arrêter l'agent : on saute le tour
        return {}
    return clean_bids(raw_bids, set(auctions), gold)


# vendre des points dans une zone protégée : au moindre souci, on ne vend rien
def safe_sale(brain: Brain, current_round: Round) -> int:
    """The cleaned number of points to sell, or 0 if anything goes wrong"""
    try:
        raw_sale = brain.decide_sale(current_round.points, current_round.gold_per_point, current_round.bank_state)
    except Exception:  # noqa: BLE001
        return 0
    return clean_sale(raw_sale, current_round.points)


# but : répondre à un message du serveur, quoi qu'il arrive, avec une réponse toujours valide
def play_round(brain: Brain, text: Any, agent_id: str) -> dict:
    """The answer to send for one raw server message, whatever happens"""
    no_bids = {"bids": {}, "points_to_spend": 0}
    try:
        current_round = read_round(text, agent_id)
        if current_round is None:
            return no_bids
        bids = safe_decide(
            brain,
            current_round.gold,
            current_round.auctions,
            current_round.prev_auctions,
            current_round.bank_state,
        )
        sale = safe_sale(brain, current_round)
        return {"bids": bids, "points_to_spend": sale}
    except Exception:  # noqa: BLE001
        # dernier filet : même un bug dans l'airbag ne doit pas arrêter l'agent
        return no_bids
