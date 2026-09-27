"""Reads live instructions from the control panel, bounded before they touch the brain (think: the radio from the control tower)"""

import json
from dataclasses import replace
from pathlib import Path

from smaug.agent.config import Settings

MARGIN_RANGE = (0.0, 1.0)
MIN_EXPECTED_VALUE_RANGE = (0.0, 20.0)
HISTORY_ROUNDS_RANGE = (1, 100)


def bounded(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class ControlFile:
    """Remembers the last valid instructions, so a broken file changes nothing"""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.last_valid_instructions: dict = {}

    def read(self) -> dict:
        try:
            instructions = json.loads(self.path.read_text())
        except (OSError, ValueError, RecursionError):
            return self.last_valid_instructions
        if not isinstance(instructions, dict):
            return self.last_valid_instructions
        self.last_valid_instructions = instructions
        return instructions


def apply_control(base_settings: Settings, instructions: dict) -> tuple[Settings, bool]:
    """Base settings adjusted by live instructions, and whether the agent should pause"""
    settings = base_settings

    margin = instructions.get("margin")
    if isinstance(margin, (int, float)):
        settings = replace(settings, margin=bounded(margin, *MARGIN_RANGE))

    min_expected_value = instructions.get("min_expected_value")
    if isinstance(min_expected_value, (int, float)):
        settings = replace(
            settings, min_expected_value=bounded(min_expected_value, *MIN_EXPECTED_VALUE_RANGE)
        )

    history_rounds = instructions.get("history_rounds")
    if isinstance(history_rounds, (int, float)):
        settings = replace(settings, history_rounds=int(bounded(history_rounds, *HISTORY_ROUNDS_RANGE)))

    paused = instructions.get("pause") is True
    return settings, paused


def settings_for_this_round(control_file: ControlFile, base_settings: Settings) -> tuple[Settings, bool]:
    """The settings to play with this round, never raising"""
    try:
        instructions = control_file.read()
        return apply_control(base_settings, instructions)
    except Exception:  # noqa: BLE001
        # la radio ne doit jamais arrêter l'agent : réglages d'usine, sans pause
        return base_settings, False
