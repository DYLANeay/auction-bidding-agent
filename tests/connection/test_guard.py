import socket
from collections.abc import Callable

from smaug.agent.connection.guard import is_previous_game_over, may_connect
from smaug.agent.connection.settings import ConnectionSettings


def never_asked(question: str) -> str:
    raise AssertionError("the question should not be asked")


# fabrique une fausse personne qui répond toujours la même chose
def always_answer(reply: str) -> Callable[[str], str]:
    def ask(question: str) -> str:
        return reply

    return ask


def test_no_question_when_the_game_is_running_or_the_board_is_unreachable() -> None:
    assert may_connect(False, never_asked)
    assert may_connect(None, never_asked)


def test_a_finished_game_needs_your_permission() -> None:
    assert may_connect(True, always_answer("y"))
    assert not may_connect(True, always_answer("n"))
    assert not may_connect(True, always_answer(""))


def test_a_finished_game_accepts_french_and_english_answers() -> None:
    for reply in ["y", "yes", "o", "oui", " Y "]:
        assert may_connect(True, always_answer(reply))


def test_an_unreachable_server_does_not_crash_the_guard() -> None:
    # un port libre, où personne n'écoute
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        free_port = probe.getsockname()[1]
    settings = ConnectionSettings("localhost", free_port, "play123", "Smaug", "test")
    assert is_previous_game_over(settings) is None
