from dataclasses import replace

from smaug.agent.config import DEFAULT_SETTINGS
from smaug.agent.planning import current_margin, is_endgame, reserve, spending_budget


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
