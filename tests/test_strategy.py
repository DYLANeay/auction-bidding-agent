from dataclasses import replace

from smaug.agent.config import DEFAULT_SETTINGS
from smaug.agent.strategy import (
    choose_bids,
    current_margin,
    expected_value,
    is_endgame,
    market_price,
    reserve,
    round_price_per_point,
    spending_budget,
)


def test_expected_value_of_known_auctions() -> None:
    assert expected_value({"die": 6, "num": 3, "bonus": 7}) == 17.5
    assert expected_value({"die": 12, "num": 4, "bonus": 2}) == 28
    assert expected_value({"die": 2, "num": 1, "bonus": 0}) == 1.5


def test_expected_value_can_be_negative() -> None:
    assert expected_value({"die": 3, "num": 1, "bonus": -8}) == -6


def test_expected_value_matches_the_average_of_every_possible_roll() -> None:
    # 2d4+1 has 16 equally likely outcomes
    total = 0
    for first_die in range(1, 5):
        for second_die in range(1, 5):
            total += first_die + second_die + 1
    average = total / 16

    assert expected_value({"die": 4, "num": 2, "bonus": 1}) == average


def test_round_price_is_the_median_of_winning_prices() -> None:
    prev_auctions = {
        "a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]},  # 700 / 17.5 = 40
        "a2": {"die": 12, "num": 4, "bonus": 2, "bids": [{"a_id": "y", "gold": 1400}]},  # 1400 / 28 = 50
    }
    assert round_price_per_point(prev_auctions, min_expected_value=2.0) == 45


def test_round_price_ignores_auctions_without_bids_and_tiny_values() -> None:
    prev_auctions = {
        "a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]},  # 40
        "a2": {"die": 6, "num": 3, "bonus": 7, "bids": []},  # personne n'a misé
        "a3": {"die": 2, "num": 1, "bonus": 0, "bids": [{"a_id": "z", "gold": 600}]},  # EV 1.5, prix absurde
    }
    assert round_price_per_point(prev_auctions, min_expected_value=2.0) == 40


def test_round_price_is_none_when_nothing_was_won() -> None:
    assert round_price_per_point({}, min_expected_value=2.0) is None


def test_market_price_uses_the_default_without_history() -> None:
    assert market_price([], default_price=20.0) == 20.0


def test_market_price_resists_a_spike() -> None:
    assert market_price([38.0, 40.0, 1000.0], default_price=20.0) == 40.0


def test_reserve_keeps_the_whole_bank_limit_mid_game() -> None:
    assert reserve(bank_limit=5000, rounds_left=500, settings=DEFAULT_SETTINGS) == 5000


def test_reserve_follows_the_reserve_factor() -> None:
    half_savings = replace(DEFAULT_SETTINGS, reserve_factor=0.5)
    assert reserve(bank_limit=5000, rounds_left=500, settings=half_savings) == 2500


def test_reserve_melts_between_110_and_10_useful_rounds_left() -> None:
    assert reserve(bank_limit=5000, rounds_left=111, settings=DEFAULT_SETTINGS) == 5000  # pas encore
    assert reserve(bank_limit=5000, rounds_left=61, settings=DEFAULT_SETTINGS) == 2500  # à moitié
    assert reserve(bank_limit=5000, rounds_left=12, settings=DEFAULT_SETTINGS) == 50
    assert reserve(bank_limit=5000, rounds_left=11, settings=DEFAULT_SETTINGS) == 0  # fondue avant le pic


def test_reserve_is_empty_on_the_last_useful_round_and_the_phantom_round() -> None:
    assert reserve(bank_limit=5000, rounds_left=2, settings=DEFAULT_SETTINGS) == 0
    assert reserve(bank_limit=5000, rounds_left=1, settings=DEFAULT_SETTINGS) == 0


def test_reserve_survives_odd_settings() -> None:
    # réglages qu'on pourrait taper par erreur depuis le TUI
    no_finish = replace(DEFAULT_SETTINGS, endgame_finish_rounds=0)
    assert reserve(bank_limit=5000, rounds_left=2, settings=no_finish) == 0
    no_melt = replace(DEFAULT_SETTINGS, endgame_rounds=0)
    assert reserve(bank_limit=5000, rounds_left=500, settings=no_melt) == 5000


def test_endgame_starts_110_useful_rounds_before_the_end() -> None:
    assert not is_endgame(rounds_left=500, settings=DEFAULT_SETTINGS)
    assert not is_endgame(rounds_left=112, settings=DEFAULT_SETTINGS)
    assert is_endgame(rounds_left=111, settings=DEFAULT_SETTINGS)
    assert is_endgame(rounds_left=2, settings=DEFAULT_SETTINGS)


def test_margin_is_bigger_during_the_endgame() -> None:
    assert current_margin(rounds_left=500, settings=DEFAULT_SETTINGS) == 0.15
    assert current_margin(rounds_left=50, settings=DEFAULT_SETTINGS) == 0.60


def test_budget_is_the_gold_above_the_savings_and_never_negative() -> None:
    assert spending_budget(gold=7200, reserve_amount=5000) == 2200
    assert spending_budget(gold=4000, reserve_amount=5000) == 0


def test_bids_follow_the_guide_example() -> None:
    # l'exemple du guide : 2200 d'or, prix 40, marge 15 %
    auctions = {
        "a41": {"die": 12, "num": 4, "bonus": 2},  # EV 28 -> 1288
        "a37": {"die": 6, "num": 3, "bonus": 7},  # EV 17.5 -> 805
        "a50": {"die": 4, "num": 2, "bonus": -1},  # EV 4 -> 184, ne rentre plus
        "a99": {"die": 3, "num": 1, "bonus": -8},  # EV -6, filtrée
    }
    bids = choose_bids(auctions, 2200, 40, 0.15, DEFAULT_SETTINGS, is_last_useful_round=False)
    assert bids == {"a41": 1288, "a37": 805}


def test_bids_skip_what_is_too_expensive_but_take_smaller_auctions() -> None:
    auctions = {
        "big": {"die": 12, "num": 4, "bonus": 2},  # 1288, trop cher
        "small": {"die": 4, "num": 2, "bonus": -1},  # 184
    }
    bids = choose_bids(auctions, 500, 40, 0.15, DEFAULT_SETTINGS, is_last_useful_round=False)
    assert bids == {"small": 184}


def test_no_bids_without_budget() -> None:
    auctions = {"a1": {"die": 6, "num": 3, "bonus": 7}}
    assert choose_bids(auctions, 0, 40, 0.15, DEFAULT_SETTINGS, is_last_useful_round=False) == {}


def test_last_useful_round_puts_the_leftover_on_the_best_auction() -> None:
    auctions = {
        "a41": {"die": 12, "num": 4, "bonus": 2},  # 1288
        "a37": {"die": 6, "num": 3, "bonus": 7},  # 805
    }
    bids = choose_bids(auctions, 2500, 40, 0.15, DEFAULT_SETTINGS, is_last_useful_round=True)
    assert bids == {"a41": 1288 + 407, "a37": 805}
    assert sum(bids.values()) == 2500


def test_bids_are_python_ints() -> None:
    auctions = {"a1": {"die": 6, "num": 3, "bonus": 7}}
    bids = choose_bids(auctions, 5000, 41.7, 0.15, DEFAULT_SETTINGS, is_last_useful_round=True)
    for bid in bids.values():
        assert type(bid) is int
