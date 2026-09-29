"""The levers write a clean control.json that the agent understands, one step at a time"""

import asyncio
import json

from smaug.agent.config import DEFAULT_SETTINGS
from smaug.agent.control import ControlFile, apply_control
from smaug.tui.app import MonitorApp
from smaug.tui.controls import (
    describe,
    is_selling,
    nudge,
    read_instructions,
    with_pause,
    with_preset,
    with_selling,
    write_instructions,
)


def test_nudge_starts_from_the_factory_setting() -> None:
    assert nudge({}, "margin", 1) == {"margin": 0.35}
    assert nudge({}, "history_rounds", -1) == {"history_rounds": 5}
    assert nudge({"min_expected_value": 8}, "min_expected_value", 1) == {"min_expected_value": 9.0}


def test_nudge_stays_inside_the_agent_limits() -> None:
    assert nudge({"margin": 1.0}, "margin", 1) == {"margin": 1.0}
    assert nudge({"history_rounds": 5}, "history_rounds", -1) == {"history_rounds": 1}
    assert nudge({"margin": "junk"}, "margin", -1) == {"margin": 0.25}


def test_a_preset_keeps_the_pause() -> None:
    assert with_preset({"pause": True, "margin": 0.9}, "mixed") == {"min_expected_value": 2.0, "margin": 0.3, "pause": True}
    assert with_preset({"margin": 0.9}, "normal") == {}


def test_pause_and_resume() -> None:
    assert with_pause({"margin": 0.4}, True) == {"margin": 0.4, "pause": True}
    assert with_pause({"margin": 0.4, "pause": True}, False) == {"margin": 0.4}


def test_written_file_is_read_by_the_agent(tmp_path) -> None:
    path = tmp_path / "control.json"
    assert write_instructions(path, {"margin": 0.5, "pause": True})
    assert not (tmp_path / "control.json.tmp").exists()
    settings, paused = apply_control(DEFAULT_SETTINGS, ControlFile(path).read())
    assert settings.margin == 0.5
    assert paused is True


def test_read_instructions_tells_missing_from_broken(tmp_path) -> None:
    path = tmp_path / "control.json"
    assert read_instructions(path) == {}
    path.write_text("{broken")
    assert read_instructions(path) is None
    assert "unreadable" in describe(None)
    assert describe({}) == "empty: factory settings"
    assert describe({"margin": 0.5, "pause": True}) == "margin 50%, PAUSE"


def test_keys_write_control_json(tmp_path) -> None:
    path = tmp_path / "control.json"

    def written() -> dict:
        return json.loads(path.read_text())

    async def run() -> None:
        app = MonitorApp("localhost", 1, "Dylan", tmp_path)
        async with app.run_test() as pilot:
            await pilot.press("plus")
            assert written() == {"margin": 0.35}

            # une seule pression sur p ne met pas en pause
            await pilot.press("p")
            assert "pause" not in written()
            await pilot.press("p")
            assert written()["pause"] is True
            await pilot.press("p")
            assert "pause" not in written()

            await pilot.press("s")
            assert written()["sell_share"] == 0.0
            await pilot.press("s")
            assert "sell_share" not in written()

            await pilot.press("3")
            assert written() == {"min_expected_value": 2.0, "margin": 0.15, "history_rounds": 20, "sell_share": 0.0}
            await pilot.press("0")
            assert written() == {}

    asyncio.run(run())


def test_selling_switch_goes_off_then_back_to_the_factory_setting() -> None:
    assert is_selling({})
    off = with_selling({"margin": 0.4}, False)
    assert off == {"margin": 0.4, "sell_share": 0.0}
    assert not is_selling(off)
    assert with_selling(off, True) == {"margin": 0.4}
    assert describe(off) == "margin 40%, selling off"


def test_the_first_version_preset_does_not_sell() -> None:
    assert not is_selling(with_preset({}, "v1"))
    assert is_selling(with_preset({}, "mixed"))
