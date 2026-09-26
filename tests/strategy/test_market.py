from smaug.agent.strategy.market import market_price, round_price_per_point


def test_round_price_is_the_median_of_winning_prices() -> None:
    prev_auctions = {
        "a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]},  # 700 / 17.5 = 40
        "a2": {"die": 12, "num": 4, "bonus": 2, "bids": [{"a_id": "y", "gold": 1400}]},  # 1400 / 28 = 50
    }
    assert round_price_per_point(prev_auctions, min_expected_value=2.0) == 45


def test_round_price_ignores_auctions_without_bids_and_tiny_values() -> None:
    prev_auctions = {
        "a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]},  # 40
        "a2": {"die": 6, "num": 3, "bonus": 7, "bids": []},  # personne n'a misé
        "a3": {"die": 2, "num": 1, "bonus": 0, "bids": [{"a_id": "z", "gold": 600}]},  # EV 1.5, prix absurde
    }
    assert round_price_per_point(prev_auctions, min_expected_value=2.0) == 40


def test_round_price_is_none_when_nothing_was_won() -> None:
    assert round_price_per_point({}, min_expected_value=2.0) is None


def test_market_price_uses_the_default_without_history() -> None:
    assert market_price([], default_price=20.0) == 20.0


def test_market_price_resists_a_spike() -> None:
    assert market_price([38.0, 40.0, 1000.0], default_price=20.0) == 40.0
