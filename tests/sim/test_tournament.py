from pathlib import Path

import pytest

from smaug.sim.tournament import grade_summary, main, play_one_job


def test_grade_summary_counts_each_grade() -> None:
    assert grade_summary(["A", "C", "A", "D"]) == "A2 C1 D1"
    assert grade_summary([]) == ""


def test_one_job_finds_our_place() -> None:
    variant_name, class_name, place, grade = play_one_job(("current", "weak", 1, 30))
    assert (variant_name, class_name) == ("current", "weak")
    assert 1 <= place <= 20
    assert grade in ["A", "B", "C", "D", "E", "F"]


def test_a_tiny_tournament_writes_the_summary(tmp_path: Path) -> None:
    output = tmp_path / "tournament.md"
    main(["--games", "1", "--rounds", "30", "--output", str(output)])
    summary = output.read_text()
    assert "| current |" in summary
    assert "| min EV 6 |" in summary


def test_only_the_chosen_variants_are_played(tmp_path: Path) -> None:
    output = tmp_path / "tournament.md"
    main(["--games", "1", "--rounds", "30", "--variants", "current, combo A", "--output", str(output)])
    summary = output.read_text()
    assert "| current |" in summary
    assert "| combo A |" in summary
    assert "| min EV 6 |" not in summary


def test_an_unknown_variant_stops_before_playing() -> None:
    with pytest.raises(SystemExit):
        main(["--variants", "magic"])
