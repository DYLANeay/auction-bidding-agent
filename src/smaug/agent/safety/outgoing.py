"""Cleans what goes out to the server (think: the departures hall)"""

from smaug.agent.safety.conversion import to_whole_number

#  Brain ──▶ [clean_bids + to_whole_number] ──▶ serveur


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
