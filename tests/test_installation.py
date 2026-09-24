"""Checks the project is installed correctly (think: turning the key before driving)"""

from importlib.metadata import version

import dnd_auction_game
import smaug


def test_our_package_can_be_imported() -> None:
    assert smaug.__doc__ is not None


def test_teacher_game_is_installed() -> None:
    assert dnd_auction_game.AuctionGameClient is not None


def test_teacher_game_has_the_server_version() -> None:
    # must match the teacher's server
    assert version("dnd_auction_game") == "0.6.0"
