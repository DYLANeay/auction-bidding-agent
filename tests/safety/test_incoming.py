import json
from typing import Any

from smaug.agent.safety.incoming import (
    read_auction,
    read_auctions,
    read_bank_state,
    read_bids,
    read_gold,
    read_number_list,
    read_prev_auctions,
    read_round,
)


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


def make_message(gold: Any = 7200) -> str:
    return json.dumps({
        "states": {"me": {"gold": gold, "points": 0}},
        "auctions": {"a41": {"die": 12, "num": 4, "bonus": 2}},
        "prev_auctions": {},
        "remainder_gold_income": [1000] * 500,
        "remainder_bank_interest": [1.05] * 500,
        "remainder_bank_limit": [5000] * 500,
    })


def test_read_round_gives_a_clean_round() -> None:
    current_round = read_round(make_message(), "me")
    assert current_round is not None
    assert current_round.gold == 7200
    assert current_round.auctions == {"a41": {"die": 12, "num": 4, "bonus": 2}}


def test_read_round_skips_broken_messages() -> None:
    assert read_round("not json at all", "me") is None
    assert read_round("[1, 2, 3]", "me") is None
    assert read_round(make_message(), "someone else") is None
    assert read_round(make_message(gold="lots"), "me") is None
    assert read_round("[" * 100000, "me") is None
