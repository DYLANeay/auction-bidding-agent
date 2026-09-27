import json

from smaug.agent.connection.safe_client import rounds_left_in, why_closed_normally


def test_rounds_left_is_read_from_the_bank_future() -> None:
    message = json.dumps({"remainder_gold_income": [1000, 990, 980]})
    assert rounds_left_in(message) == 3


def test_rounds_left_survives_broken_messages() -> None:
    for text in ["not json", "[1, 2]", "{}", json.dumps({"remainder_gold_income": "lots"}), None]:
        assert rounds_left_in(text) is None


def test_a_clean_close_after_the_phantom_round_is_the_end_of_the_game() -> None:
    assert why_closed_normally(rounds_received=1000, rounds_left=1) == "game_over"


def test_a_clean_close_before_any_round_is_a_refusal() -> None:
    assert why_closed_normally(rounds_received=0, rounds_left=None) == "refused"


def test_a_clean_close_in_the_middle_of_the_game_is_a_drop() -> None:
    assert why_closed_normally(rounds_received=412, rounds_left=588) == "dropped"
