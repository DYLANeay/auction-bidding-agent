from dataclasses import replace

from smaug.agent.config import DEFAULT_SETTINGS
from smaug.agent.strategy.brain import Brain


def make_bank_state(rounds_left: int, bank_limit: int = 5000) -> dict[str, list]:
    return {
        "gold_income_per_round": [1000] * rounds_left,
        "bank_interest_per_round": [1.05] * rounds_left,
        "bank_limit_per_round": [bank_limit] * rounds_left,
    }


def test_brain_keeps_only_the_last_rounds_in_memory() -> None:
    brain = Brain(replace(DEFAULT_SETTINGS, history_rounds=3))
    prev_auctions = {"a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}}
    for _ in range(5):
        brain.remember_prices(prev_auctions)
    assert brain.price_history == [40, 40, 40]


def test_brain_does_not_bid_on_the_phantom_round() -> None:
    auctions = {"a1": {"die": 6, "num": 3, "bonus": 7}}
    assert Brain().decide(9000, auctions, {}, make_bank_state(rounds_left=1)) == {}


def test_brain_saves_first_then_bids_with_the_surplus() -> None:
    auctions = {"a41": {"die": 12, "num": 4, "bonus": 2}}  # EV 28
    prev_auctions = {"a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}}  # prix 40
    brain = Brain()

    # 4000 d'or, épargne de 5000 : rien à dépenser
    assert brain.decide(4000, auctions, prev_auctions, make_bank_state(rounds_left=500)) == {}
    # 7200 d'or : 2200 au-dessus de l'épargne, la mise de 1288 passe
    assert brain.decide(7200, auctions, prev_auctions, make_bank_state(rounds_left=500)) == {"a41": 1288}
