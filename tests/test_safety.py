import numpy as np

from smaug.agent.safety import clean_bids, to_whole_number


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
