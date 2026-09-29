from smaug.agent.config import DEFAULT_SETTINGS, NO_SELLING_SETTINGS, Settings
from smaug.agent.strategy.selling import points_to_sell

SELLING = Settings(sell_share=0.01)
MID_GAME = 500


def test_nothing_is_sold_when_selling_is_off() -> None:
    assert points_to_sell(10_000, 40, 20, MID_GAME, NO_SELLING_SETTINGS) == 0


def test_the_factory_settings_sell_two_percent() -> None:
    assert points_to_sell(10_000, 40, 20, MID_GAME, DEFAULT_SETTINGS) == 200


def test_a_small_share_is_sold_when_the_bank_pays_twice_our_price() -> None:
    assert points_to_sell(10_000, 40, 20, MID_GAME, SELLING) == 100


def test_nothing_is_sold_when_the_bank_does_not_pay_enough() -> None:
    # 1,5 fois notre prix ne suffit pas : il faut au moins 2 fois
    assert points_to_sell(10_000, 30, 20, MID_GAME, SELLING) == 0


def test_nothing_is_sold_at_a_suspicious_rate() -> None:
    assert points_to_sell(10_000, 200, 20, MID_GAME, SELLING) == 0


def test_nothing_is_sold_during_the_endgame() -> None:
    assert points_to_sell(10_000, 40, 20, 50, SELLING) == 0


def test_a_floor_of_points_is_always_kept() -> None:
    half = Settings(sell_share=0.5)
    assert points_to_sell(520, 40, 20, MID_GAME, half) == 20
    assert points_to_sell(400, 40, 20, MID_GAME, half) == 0


def test_no_market_price_means_no_sale() -> None:
    assert points_to_sell(10_000, 40, 0, MID_GAME, SELLING) == 0
