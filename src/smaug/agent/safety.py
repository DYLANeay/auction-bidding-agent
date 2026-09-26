"""Checks everything going in and out of the brain (think: airport security)"""

import math
from typing import Any
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
