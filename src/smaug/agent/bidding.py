"""Which auctions to bid on, and how much (think: walking the auction room with your wallet)"""

from smaug.agent.config import Settings
from smaug.agent.values import expected_value


def choose_bids(
    auctions: dict[str, dict],
    budget: float,
    price_per_point: float,
    margin: float,
    settings: Settings,
    is_last_useful_round: bool,
) -> dict[str, int]:
    """Bids on the most valuable auctions first, as long as the budget allows"""
    candidates = []
    # on écarte les enchères pas rentables
    for auction_id, auction in auctions.items():
        value = expected_value(auction)
        if value >= settings.min_expected_value:
            candidates.append((value, auction_id))
    # les tuples se trient sur leur premier élément : la valeur, la plus grande d'abord
    candidates.sort(reverse=True)

    bids = {}
    remaining = budget
    # on mise sur les enchères les plus intéressantes tant qu'on a de l'argent
    for value, auction_id in candidates:
        bid = round(value * price_per_point * (1 + margin))
        if bid < 1 or bid > remaining:
            continue
        bids[auction_id] = bid
        remaining -= bid

    # dernier tour utile : l'or restant ne vaudra plus rien, gros coup sur la meilleure enchère
    if is_last_useful_round and len(candidates) > 0:
        leftover = int(remaining)
        if leftover >= 1:
            best_id = candidates[0][1]
            bids[best_id] = bids.get(best_id, 0) + leftover

    return bids
