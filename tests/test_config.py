from dataclasses import FrozenInstanceError, replace

import pytest

from smaug.agent.config import DEFAULT_SETTINGS, V1_SETTINGS


def test_defaults_are_the_tournament_winner() -> None:
    assert DEFAULT_SETTINGS.min_expected_value == 8.0
    assert DEFAULT_SETTINGS.history_rounds == 10
    assert DEFAULT_SETTINGS.margin == 0.30
    assert DEFAULT_SETTINGS.endgame_rounds == 100
    assert DEFAULT_SETTINGS.endgame_finish_rounds == 10
    assert DEFAULT_SETTINGS.endgame_margin == 0.60
    # la vente de points reste éteinte tant que le tournoi n'a pas prouvé un gain
    assert DEFAULT_SETTINGS.sell_share == 0.0


def test_settings_cannot_be_changed_by_accident() -> None:
    with pytest.raises(FrozenInstanceError):
        DEFAULT_SETTINGS.margin = 0.5  # pyright: ignore[reportAttributeAccessIssue]


def test_replace_gives_new_settings_and_keeps_the_defaults() -> None:
    aggressive = replace(DEFAULT_SETTINGS, margin=0.5)
    assert aggressive.margin == 0.5
    assert DEFAULT_SETTINGS.margin == 0.30


def test_the_first_version_is_kept_for_comparison() -> None:
    assert V1_SETTINGS.min_expected_value == 2.0
    assert V1_SETTINGS.history_rounds == 20
    assert V1_SETTINGS.margin == 0.15
    assert V1_SETTINGS.reserve_factor == DEFAULT_SETTINGS.reserve_factor
