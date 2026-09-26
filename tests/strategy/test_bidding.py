from smaug.agent.config import DEFAULT_SETTINGS
from smaug.agent.strategy.bidding import choose_bids


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
