import numpy as np

from smaug.agent.brain import Brain
from smaug.agent.safety import (
    clean_bids,
    read_auction,
    read_auctions,
    read_bank_state,
    read_bids,
    read_gold,
    read_number_list,
    read_prev_auctions,
    safe_decide,
    to_number,
    to_whole_number,
)


def test_whole_number_accepts_numbers_including_numpy() -> None:
    assert to_whole_number(12) == 12
    assert to_whole_number(12.9) == 12
    assert to_whole_number(np.int64(7)) == 7
    assert type(to_whole_number(np.int64(7))) is int


def test_whole_number_rejects_what_is_not_a_usable_number() -> None:
    for bad_value in [None, "abc", [], {}, True, float("nan"), float("inf")]:
        assert to_whole_number(bad_value) is None


def test_clean_bids_keeps_good_bids_as_python_ints() -> None:
    bids = clean_bids({"a1": np.int64(300), "a2": 200.0}, {"a1", "a2"}, gold=1000)
    assert bids == {"a1": 300, "a2": 200}
    for bid in bids.values():
        assert type(bid) is int


def test_clean_bids_drops_unknown_auctions_and_bad_amounts() -> None:
    raw_bids = {"a1": 300, "ghost": 100, "a2": 0, "a3": -50, "a4": "lots"}
    assert clean_bids(raw_bids, {"a1", "a2", "a3", "a4"}, gold=1000) == {"a1": 300}


def test_clean_bids_never_exceed_our_gold() -> None:
    bids = clean_bids({"a1": 700, "a2": 500, "a3": 200}, {"a1", "a2", "a3"}, gold=1000)
    assert bids == {"a1": 700, "a3": 200}
    assert sum(bids.values()) <= 1000


def test_clean_bids_of_garbage_is_empty() -> None:
    assert clean_bids(None, {"a1"}, gold=1000) == {}
    assert clean_bids(["a1", 300], {"a1"}, gold=1000) == {}


class BrokenBrain(Brain):
    def decide(self, gold, auctions, prev_auctions, bank_state):
        raise ZeroDivisionError("bug in the brain")


class SloppyBrain(Brain):
    def decide(self, gold, auctions, prev_auctions, bank_state):
        return {"a1": np.float64(250.7), "ghost": 100, "a2": 99999}


BANK_STATE = {
    "gold_income_per_round": [1000] * 500,
    "bank_interest_per_round": [1.05] * 500,
    "bank_limit_per_round": [5000] * 500,
}
AUCTIONS = {"a1": {"die": 6, "num": 3, "bonus": 7}, "a2": {"die": 12, "num": 4, "bonus": 2}}


def test_safe_decide_skips_the_round_when_the_brain_crashes() -> None:
    assert safe_decide(BrokenBrain(), 9000, AUCTIONS, {}, BANK_STATE) == {}


def test_safe_decide_cleans_a_sloppy_answer() -> None:
    assert safe_decide(SloppyBrain(), 1000, AUCTIONS, {}, BANK_STATE) == {"a1": 250}


def test_safe_decide_lets_a_good_answer_through() -> None:
    bids = safe_decide(Brain(), 9000, AUCTIONS, {}, BANK_STATE)
    assert len(bids) > 0


def test_read_auction_keeps_good_dice() -> None:
    assert read_auction({"die": 6, "num": 3, "bonus": 7}) == {"die": 6, "num": 3, "bonus": 7}
    assert read_auction({"die": "6", "num": 3.0, "bonus": -2}) == {"die": 6, "num": 3, "bonus": -2}


def test_read_auction_rejects_broken_or_absurd_dice() -> None:
    broken = [
        None,
        "3d6+7",
        {"die": 6, "num": 3},  # bonus manquant
        {"die": 0, "num": 3, "bonus": 7},  # dé à 0 face
        {"die": 6, "num": 3, "bonus": None},
        {"die": 10**12, "num": 3, "bonus": 7},
        {"die": 6, "num": -1, "bonus": 7},
    ]
    for raw in broken:
        assert read_auction(raw) is None


def test_read_bids_sorts_highest_first_and_drops_broken_bids() -> None:
    raw_bids = [{"a_id": "x", "gold": 100}, {"a_id": "y", "gold": 700}, {"gold": "lots"}, "junk"]
    assert read_bids(raw_bids) == [{"a_id": "y", "gold": 700}, {"a_id": "x", "gold": 100}]


def test_read_auctions_skips_broken_auctions_only() -> None:
    raw = {"a1": {"die": 6, "num": 3, "bonus": 7}, "a2": "broken", 42: {"die": 6, "num": 1, "bonus": 0}}
    assert read_auctions(raw) == {"a1": {"die": 6, "num": 3, "bonus": 7}}


def test_read_prev_auctions_keeps_clean_results() -> None:
    raw = {"a1": {"die": 6, "num": 3, "bonus": 7, "reward": 15, "bids": [{"a_id": "x", "gold": 700}]}}
    assert read_prev_auctions(raw) == {
        "a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}
    }


def test_read_functions_survive_garbage() -> None:
    for garbage in [None, 42, "text", [1, 2], {"a1": None}]:
        assert read_auctions(garbage) == {}
        assert read_prev_auctions(garbage) == {}


def test_to_number_keeps_decimals() -> None:
    assert to_number(1.05) == 1.05
    assert to_number("2.5") == 2.5
    assert to_number(float("nan")) is None


def test_read_number_list_refuses_any_broken_value() -> None:
    assert read_number_list([1000, 980.5]) == [1000.0, 980.5]
    assert read_number_list([1000, "abc"]) is None
    assert read_number_list([]) is None
    assert read_number_list(None) is None


def test_read_bank_state_builds_the_brain_format() -> None:
    message = {
        "remainder_gold_income": [1000, 990],
        "remainder_bank_interest": [1.05, 1.04],
        "remainder_bank_limit": [5000, 5100],
    }
    assert read_bank_state(message) == {
        "gold_income_per_round": [1000.0, 990.0],
        "bank_interest_per_round": [1.05, 1.04],
        "bank_limit_per_round": [5000.0, 5100.0],
    }


def test_read_bank_state_refuses_a_broken_bank() -> None:
    assert read_bank_state({}) is None
    broken_limit = {
        "remainder_gold_income": [1000],
        "remainder_bank_interest": [1.05],
        "remainder_bank_limit": [-5000],
    }
    assert read_bank_state(broken_limit) is None


def test_read_gold_finds_our_gold_or_gives_up() -> None:
    states = {"me": {"gold": 7200, "points": 30}, "other": {"gold": 100, "points": 5}}
    assert read_gold(states, "me") == 7200
    assert read_gold(states, "ghost") is None
    assert read_gold({"me": {"gold": "rich"}}, "me") is None
    assert read_gold({"me": {"gold": -10}}, "me") is None
    assert read_gold(None, "me") is None
