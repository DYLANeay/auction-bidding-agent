"""How much a point costs right now (think: the price board at the market)"""

from statistics import median

from smaug.agent.values import expected_value


# prix médian payé par point au tour précédent
def round_price_per_point(prev_auctions: dict[str, dict], min_expected_value: float) -> float | None:
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


# médiane des prix des derniers tours (la fenêtre est gérée par le Brain), ou prix par défaut sans historique
def market_price(price_history: list[float], default_price: float) -> float:
    """Median of the recent round prices, or the default before any history"""
    # la médiane plutôt que la moyenne résiste aux valeurs aberrantes (ex : un joueur qui paie 1000 par point au lieu de 40)
    if len(price_history) == 0:
        return default_price
    return median(price_history)
