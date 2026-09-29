from collections.abc import Callable

from smaug.agent.connection.leftover import clear_unless_kept, leftover_instructions


def never_asked(question: str) -> str:
    raise AssertionError("the question should not be asked")


def always_answer(reply: str) -> Callable[[str], str]:
    def ask(question: str) -> str:
        return reply

    return ask


def nobody_at_the_keyboard(question: str) -> str:
    raise EOFError


def test_nothing_to_say_when_the_file_is_missing_empty_or_blank(tmp_path) -> None:
    path = tmp_path / "control.json"
    assert leftover_instructions(path) is None
    path.write_text("")
    assert leftover_instructions(path) is None
    path.write_text(" { } \n")
    assert leftover_instructions(path) is None
    assert not clear_unless_kept(path, None, never_asked)


def test_a_real_instruction_is_shown_on_one_line(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text('{\n  "margin": 0.2\n}')
    assert leftover_instructions(path) == '{ "margin": 0.2 }'


def test_a_broken_file_is_shown_too(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text("{margin")
    assert leftover_instructions(path) == "{margin"
    path.write_text("[" * 100_000)
    assert leftover_instructions(path) == "[" * 200


def test_pressing_enter_clears_the_file(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text('{"margin": 0.2}')
    assert clear_unless_kept(path, leftover_instructions(path), always_answer(""))
    assert path.read_text() == "{}"


def test_yes_keeps_the_file(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text('{"margin": 0.2}')
    for reply in ["y", "yes", "o", " OUI "]:
        assert not clear_unless_kept(path, leftover_instructions(path), always_answer(reply))
    assert path.read_text() == '{"margin": 0.2}'


def test_without_a_keyboard_the_file_is_cleared_instead_of_crashing(tmp_path) -> None:
    path = tmp_path / "control.json"
    path.write_text('{"pause": true}')
    assert clear_unless_kept(path, leftover_instructions(path), nobody_at_the_keyboard)
    assert path.read_text() == "{}"


def test_a_file_that_cannot_be_written_does_not_crash(tmp_path) -> None:
    path = tmp_path / "missing_folder" / "control.json"
    assert not clear_unless_kept(path, '{"margin": 0.2}', always_answer(""))
