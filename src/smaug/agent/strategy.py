"""The brain: pure decisions from the game state (think: the buyer's head, no phone, no network)"""


def expected_value(auction: dict[str, int]) -> float:
    """Average points of an auction like 3d6+7"""
    average_roll = (auction["die"] + 1) / 2
    return average_roll * auction["num"] + auction["bonus"]
