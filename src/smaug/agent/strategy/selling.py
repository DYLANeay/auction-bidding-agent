"""When to sell a few points to the bank for gold (think: a shop selling stock when the wholesaler pays too much)"""

import math

from smaug.agent.config import Settings
from smaug.agent.strategy.planning import is_endgame

# jamais sous ce stock de points : aucune note F possible (points <= 10)
MIN_POINTS_KEPT = 500
# au-delà, le taux est suspect (le prof annonce des données piégées)
MAX_RATE_RATIO = 5.0


def points_to_sell(
    points: int,
    gold_per_point: float,
    market_price: float,
    rounds_left: int,
    settings: Settings,
) -> int:
    """How many points to sell to the bank this round, 0 most of the time"""
    if settings.sell_share <= 0:
        return 0
    # en fin de partie, l'or ne se retransforme presque plus en points
    if is_endgame(rounds_left, settings):
        return 0
    if market_price <= 0:
        return 0
    ratio = gold_per_point / market_price
    if ratio < settings.sell_ratio or ratio > MAX_RATE_RATIO:
        return 0
    sellable = points - MIN_POINTS_KEPT
    if sellable <= 0:
        return 0
    batch = math.floor(points * settings.sell_share)
    return min(batch, sellable)
