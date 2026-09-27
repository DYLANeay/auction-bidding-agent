from smaug.agent.connection.reconnect import should_call_back


def test_never_call_back_after_the_game_or_a_refusal() -> None:
    assert not should_call_back("game_over", last_rounds_left=588, last_message_at=100.0, now=101.0)
    assert not should_call_back("refused", last_rounds_left=None, last_message_at=None, now=101.0)


def test_keep_trying_while_the_game_has_not_started() -> None:
    assert should_call_back("unreachable", last_rounds_left=None, last_message_at=None, now=101.0)
    assert should_call_back("dropped", last_rounds_left=None, last_message_at=None, now=101.0)


def test_call_back_after_a_drop_in_the_middle_of_the_game() -> None:
    # coupure au tour 412, il y a 3 secondes
    assert should_call_back("dropped", last_rounds_left=588, last_message_at=100.0, now=103.0)


def test_do_not_call_back_too_close_to_the_end() -> None:
    assert not should_call_back("dropped", last_rounds_left=4, last_message_at=100.0, now=100.5)


def test_do_not_call_back_if_the_game_may_already_be_over() -> None:
    # 588 tours restaient, mais le dernier message date d'il y a 10 minutes
    assert not should_call_back("dropped", last_rounds_left=588, last_message_at=100.0, now=700.0)
