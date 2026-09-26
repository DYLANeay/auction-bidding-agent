from smaug.agent.values import expected_value


def test_expected_value_of_known_auctions() -> None:
    assert expected_value({"die": 6, "num": 3, "bonus": 7}) == 17.5
    assert expected_value({"die": 12, "num": 4, "bonus": 2}) == 28
    assert expected_value({"die": 2, "num": 1, "bonus": 0}) == 1.5


def test_expected_value_can_be_negative() -> None:
    assert expected_value({"die": 3, "num": 1, "bonus": -8}) == -6


def test_expected_value_matches_the_average_of_every_possible_roll() -> None:
    # 2d4+1 has 16 equally likely outcomes
    total = 0
    for first_die in range(1, 5):
        for second_die in range(1, 5):
            total += first_die + second_die + 1
    average = total / 16

    assert expected_value({"die": 4, "num": 2, "bonus": 1}) == average
