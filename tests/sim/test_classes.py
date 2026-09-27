import random

from smaug.sim.classes import CLASSES, OUR_NAME, clone
from smaug.sim.engine import play_game
from smaug.sim.players import OurAgent


def test_every_class_has_20_players_with_us_first() -> None:
    for make_class in CLASSES.values():
        players = make_class()
        assert len(players) == 20
        assert players[0].name == OUR_NAME
        names = [player.name for player in players]
        assert len(set(names)) == 20


def test_clones_have_different_settings() -> None:
    random.seed(1)
    first = clone(0)
    second = clone(1)
    assert isinstance(first, OurAgent) and isinstance(second, OurAgent)
    assert first.brain.settings != second.brain.settings


def test_every_class_plays_a_short_game() -> None:
    for make_class in CLASSES.values():
        ranking = play_game(make_class, rounds=30, seed=1)
        assert len(ranking) == 20
