import pytest

from smaug.sim.grades import grade_for
from smaug.sim.run_one import main


def test_grades_match_the_scoreboard_for_20_players() -> None:
    grades = [grade_for(place_index, 20, points=1000) for place_index in range(20)]
    assert grades == ["A"] * 3 + ["B"] * 2 + ["C"] * 3 + ["D"] * 4 + ["E"] * 8


def test_ten_points_or_less_is_an_f_whatever_the_place() -> None:
    assert grade_for(0, 20, points=10) == "F"
    assert grade_for(0, 20, points=11) == "A"


def test_make_sim_prints_the_ranking(capsys: pytest.CaptureFixture[str]) -> None:
    main(["--class", "weak", "--rounds", "30", "--seed", "2"])
    output = capsys.readouterr().out
    assert "weak class, 30 rounds, seed 2" in output
    assert "<- us" in output
