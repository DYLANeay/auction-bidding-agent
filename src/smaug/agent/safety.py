"""Checks everything going in and out of the brain (think: airport security)"""

import math
from typing import Any

from smaug.agent.brain import Brain

#
#  Brain ──▶ [clean_bids + to_whole_number] ──▶ serveur
# « est-ce vraiment un nombre utilisable ? »


def to_whole_number(value: Any) -> int | None:
    """A plain Python int from any number, or None if it is not a usable number"""
    # True et False sont des nombres pour Python, jamais pour nous
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    # rejette NaN et l'infini
    if not math.isfinite(number):
        return None
    return int(number)


# « ne laisser partir que des mises valides »
def clean_bids(raw_bids: object, auction_ids: set[str], gold: int) -> dict[str, int]:
    """Only valid bids: Python ints of at least 1, on this round's auctions, within our gold"""
    if not isinstance(raw_bids, dict):
        return {}

    cleaned = {}
    remaining = gold
    for auction_id, raw_bid in raw_bids.items():
        if auction_id not in auction_ids:
            continue
        bid = to_whole_number(raw_bid)
        if bid is None or bid < 1:
            continue
        # le serveur ignore en silence une mise qui dépasse l'or restant
        if bid > remaining:
            continue
        cleaned[auction_id] = bid
        remaining -= bid
    return cleaned


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
