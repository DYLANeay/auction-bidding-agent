import numpy as np

from smaug.agent.safety.conversion import to_number, to_whole_number


def test_whole_number_accepts_numbers_including_numpy() -> None:
    assert to_whole_number(12) == 12
    assert to_whole_number(12.9) == 12
    assert to_whole_number(np.int64(7)) == 7
    assert type(to_whole_number(np.int64(7))) is int


def test_whole_number_rejects_what_is_not_a_usable_number() -> None:
    for bad_value in [None, "abc", [], {}, True, float("nan"), float("inf")]:
        assert to_whole_number(bad_value) is None


def test_to_number_keeps_decimals() -> None:
    assert to_number(1.05) == 1.05
    assert to_number("2.5") == 2.5
    assert to_number(float("nan")) is None
