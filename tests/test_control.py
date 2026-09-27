"""Live instructions are bounded, and a broken file keeps the last valid ones"""

from smaug.agent.config import DEFAULT_SETTINGS, Settings
from smaug.agent.control import ControlFile, apply_control


def test_no_instructions_keeps_the_tournament_settings() -> None:
    settings, paused = apply_control(DEFAULT_SETTINGS, {})
    assert settings == DEFAULT_SETTINGS
    assert paused is False


def test_apply_control_bounds_the_margin() -> None:
    settings, paused = apply_control(Settings(margin=0.3), {"margin": 5.0})
    assert settings.margin == 1.0
    assert paused is False


def test_apply_control_ignores_junk_values() -> None:
    settings, _ = apply_control(Settings(margin=0.3), {"margin": "a lot"})
    assert settings.margin == 0.3


def test_apply_control_reads_the_pause_flag() -> None:
    _, paused = apply_control(Settings(), {"pause": True})
    assert paused is True


def test_control_file_keeps_the_last_valid_instructions(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text('{"margin": 0.5}')
    control_file = ControlFile(path)
    assert control_file.read() == {"margin": 0.5}

    path.write_text("not json at all")
    assert control_file.read() == {"margin": 0.5}


def test_control_file_tolerates_a_missing_file(tmp_path) -> None:
    control_file = ControlFile(tmp_path / "missing.json")
    assert control_file.read() == {}
