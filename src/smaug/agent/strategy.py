"""The brain: pure decisions from the game state (think: the buyer's head, no phone, no network)"""

from statistics import median


def expected_value(auction: dict[str, int]) -> float:
    """Average points of an auction like 3d6+7"""
    average_roll = (auction["die"] + 1) / 2
    return average_roll * auction["num"] + auction["bonus"]


# calculates the median price per point in the previous round
def round_price_per_point(
    prev_auctions: dict[str, dict], min_expected_value: float
) -> float | None:
    """Median gold paid per point on the auctions won last round"""
    prices = []
    for auction in prev_auctions.values():
        bids = auction["bids"]
        if len(bids) == 0:
            continue
        value = expected_value(auction)
        # une EV minuscule ferait exploser le prix (division par presque 0)
        if value < min_expected_value:
            continue
        winning_bid = bids[0]["gold"]
        prices.append(winning_bid / value)

    if len(prices) == 0:
        return None
    return median(prices)


# calculates the median price of the recent round prices (number of rounds passed by the Brain class), or returns a default price if there is no history
def market_price(price_history: list[float], default_price: float) -> float:
    """Median of the recent round prices, or the default before any history"""
    """Utiliser la médiane au lieu de la moyenne sert à résister aux valeurs aberrantes (ex: un joueur qui a misé 1000 sur un objet à 40)"""
    if len(price_history) == 0:
        return default_price
    return median(price_history)
