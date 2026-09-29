import numpy as np

from smaug.agent.safety.outgoing import clean_bids, clean_sale


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


def test_clean_sale_keeps_a_sane_sale_as_a_python_int() -> None:
    sale = clean_sale(np.int64(120), points=10_000)
    assert sale == 120
    assert type(sale) is int


def test_clean_sale_never_goes_below_the_floor_of_points() -> None:
    assert clean_sale(900, points=1000) == 500
    assert clean_sale(50, points=300) == 0


def test_clean_sale_of_garbage_is_zero() -> None:
    for junk in [None, -5, "lots", float("nan"), [], True]:
        assert clean_sale(junk, points=10_000) == 0
