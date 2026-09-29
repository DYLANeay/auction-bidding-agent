from dataclasses import replace

from smaug.agent.config import V1_SETTINGS, Settings
from smaug.agent.strategy.brain import Brain


def make_bank_state(rounds_left: int, bank_limit: int = 5000) -> dict[str, list]:
    return {
        "gold_income_per_round": [1000] * rounds_left,
        "bank_interest_per_round": [1.05] * rounds_left,
        "bank_limit_per_round": [bank_limit] * rounds_left,
    }


def test_brain_keeps_only_the_last_rounds_in_memory() -> None:
    brain = Brain(replace(V1_SETTINGS, history_rounds=3))
    prev_auctions = {"a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}}
    for _ in range(5):
        brain.remember_prices(prev_auctions)
    assert brain.price_history == [40, 40, 40]


def test_brain_does_not_bid_on_the_phantom_round() -> None:
    auctions = {"a1": {"die": 6, "num": 3, "bonus": 7}}
    assert Brain(V1_SETTINGS).decide(9000, auctions, {}, make_bank_state(rounds_left=1)) == {}


def test_brain_saves_first_then_bids_with_the_surplus() -> None:
    auctions = {"a41": {"die": 12, "num": 4, "bonus": 2}}  # EV 28
    prev_auctions = {"a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}}  # prix 40
    brain = Brain(V1_SETTINGS)

    # 4000 d'or, épargne de 5000 : rien à dépenser
    assert brain.decide(4000, auctions, prev_auctions, make_bank_state(rounds_left=500)) == {}
    # 7200 d'or : 2200 au-dessus de l'épargne, la mise de 1288 passe
    assert brain.decide(7200, auctions, prev_auctions, make_bank_state(rounds_left=500)) == {"a41": 1288}


def test_brain_survives_an_absurd_history_setting() -> None:
    prev_auctions = {"a1": {"die": 6, "num": 3, "bonus": 7, "bids": [{"a_id": "x", "gold": 700}]}}
    for absurd in [0, -1, -100]:
        brain = Brain(replace(V1_SETTINGS, history_rounds=absurd))
        brain.remember_prices(prev_auctions)
        brain.remember_prices(prev_auctions)
        assert brain.price_history == [40]


def test_brain_sells_only_when_selling_is_on() -> None:
    assert Brain().decide_sale(20_000, 60.0, make_bank_state(500)) == 0
    assert Brain(Settings(sell_share=0.01)).decide_sale(20_000, 60.0, make_bank_state(500)) == 200
    # fin de partie : on garde tout
    assert Brain(Settings(sell_share=0.01)).decide_sale(20_000, 60.0, make_bank_state(50)) == 0
