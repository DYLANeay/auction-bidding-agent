from dataclasses import FrozenInstanceError, replace

import pytest

from smaug.agent.config import DEFAULT_SETTINGS


def test_defaults_match_the_v1() -> None:
    assert DEFAULT_SETTINGS.min_expected_value == 2.0
    assert DEFAULT_SETTINGS.history_rounds == 20
    assert DEFAULT_SETTINGS.margin == 0.15
    assert DEFAULT_SETTINGS.endgame_rounds == 50


def test_settings_cannot_be_changed_by_accident() -> None:
    with pytest.raises(FrozenInstanceError):
        DEFAULT_SETTINGS.margin = 0.5  # pyright: ignore[reportAttributeAccessIssue]


def test_replace_gives_new_settings_and_keeps_the_defaults() -> None:
    aggressive = replace(DEFAULT_SETTINGS, margin=0.5)
    assert aggressive.margin == 0.5
    assert DEFAULT_SETTINGS.margin == 0.15
