"""The monitor's levers: they only write logs/control.json, which the agent reads and bounds (think: the radio button in the control tower)"""

import json
import os
from pathlib import Path

from smaug.agent.config import DEFAULT_SETTINGS, V1_SETTINGS
from smaug.agent.control import HISTORY_ROUNDS_RANGE, MARGIN_RANGE, MIN_EXPECTED_VALUE_RANGE, bounded

# un pas par appui sur une touche
MARGIN_STEP = 0.05
MIN_EXPECTED_VALUE_STEP = 1.0
HISTORY_ROUNDS_STEP = 5

# les préréglages validés par le tournoi (results/expected_results.md)
PRESETS = {
    "normal": {},
    "mixed": {"min_expected_value": 2.0, "margin": 0.30},
    "v1": {
        "min_expected_value": V1_SETTINGS.min_expected_value,
        "margin": V1_SETTINGS.margin,
        "history_rounds": V1_SETTINGS.history_rounds,
    },
}

LEVERS = {
    "margin": (MARGIN_STEP, MARGIN_RANGE, DEFAULT_SETTINGS.margin),
    "min_expected_value": (MIN_EXPECTED_VALUE_STEP, MIN_EXPECTED_VALUE_RANGE, DEFAULT_SETTINGS.min_expected_value),
    "history_rounds": (HISTORY_ROUNDS_STEP, HISTORY_ROUNDS_RANGE, DEFAULT_SETTINGS.history_rounds),
}


def read_instructions(path: Path) -> dict | None:
    """What control.json asks for now: {} if there is no file, None if it cannot be read"""
    if not path.exists():
        return {}
    try:
        instructions = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, RecursionError):
        return None
    if not isinstance(instructions, dict):
        return None
    return instructions


def write_instructions(path: Path, instructions: dict) -> bool:
    """Writes the whole file at once, so the agent never reads a half-written one"""
    temporary = path.with_name(path.name + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(instructions), encoding="utf-8")
        # un renommage est atomique : l'agent voit l'ancien fichier ou le nouveau, jamais un mélange
        os.replace(temporary, path)
    except OSError:
        return False
    return True


def current_value(instructions: dict, lever: str) -> float:
    step, limits, factory_value = LEVERS[lever]
    value = instructions.get(lever)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return factory_value
    return bounded(value, limits[0], limits[1])


def nudge(instructions: dict, lever: str, direction: int) -> dict:
    """The instructions with one lever moved one step up (1) or down (-1)"""
    step, limits, factory_value = LEVERS[lever]
    moved = current_value(instructions, lever) + direction * step
    moved = bounded(moved, limits[0], limits[1])
    updated = dict(instructions)
    if lever == "history_rounds":
        updated[lever] = int(moved)
    else:
        updated[lever] = round(moved, 2)
    return updated


def with_preset(instructions: dict, preset: str) -> dict:
    """A tournament preset, keeping the pause as it was"""
    updated = dict(PRESETS[preset])
    if instructions.get("pause") is True:
        updated["pause"] = True
    return updated


def with_pause(instructions: dict, paused: bool) -> dict:
    updated = dict(instructions)
    if paused:
        updated["pause"] = True
    else:
        updated.pop("pause", None)
    return updated


def describe(instructions: dict | None) -> str:
    """control.json in a few words, for the screen"""
    if instructions is None:
        return "unreadable, the agent keeps its last valid instructions"
    if len(instructions) == 0:
        return "empty: factory settings"
    parts = []
    if "margin" in instructions:
        parts.append(f"margin {current_value(instructions, 'margin') * 100:.0f}%")
    if "min_expected_value" in instructions:
        parts.append(f"min EV {current_value(instructions, 'min_expected_value'):g}")
    if "history_rounds" in instructions:
        parts.append(f"window {current_value(instructions, 'history_rounds'):.0f}")
    if instructions.get("pause") is True:
        parts.append("PAUSE")
    if len(parts) == 0:
        return "nothing the agent understands"
    return ", ".join(parts)
