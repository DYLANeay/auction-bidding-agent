import json
from typing import Any

import numpy as np

from smaug.agent.config import Settings
from smaug.agent.safety.airbag import play_round, safe_decide, safe_sale
from smaug.agent.safety.game_round import Round
from smaug.agent.strategy.brain import Brain


class BrokenBrain(Brain):
    def decide(self, gold, auctions, prev_auctions, bank_state):
        raise ZeroDivisionError("bug in the brain")


class BrokenSeller(Brain):
    def decide_sale(self, points, gold_per_point, bank_state):
        raise ZeroDivisionError("bug in the sale")


class SloppyBrain(Brain):
    def decide(self, gold, auctions, prev_auctions, bank_state):
        return {"a1": np.float64(250.7), "ghost": 100, "a2": 99999}


BANK_STATE = {
    "gold_income_per_round": [1000] * 500,
    "bank_interest_per_round": [1.05] * 500,
    "bank_limit_per_round": [5000] * 500,
}
AUCTIONS = {"a1": {"die": 6, "num": 3, "bonus": 7}, "a2": {"die": 12, "num": 4, "bonus": 2}}


def test_safe_decide_skips_the_round_when_the_brain_crashes() -> None:
    assert safe_decide(BrokenBrain(), 9000, AUCTIONS, {}, BANK_STATE) == {}


def test_safe_decide_cleans_a_sloppy_answer() -> None:
    assert safe_decide(SloppyBrain(), 1000, AUCTIONS, {}, BANK_STATE) == {"a1": 250}


def test_safe_decide_lets_a_good_answer_through() -> None:
    bids = safe_decide(Brain(), 9000, AUCTIONS, {}, BANK_STATE)
    assert len(bids) > 0


def test_play_round_answers_with_bids() -> None:
    answer = play_round(Brain(), make_message(), "me")
    assert answer["points_to_spend"] == 0
    assert "a41" in answer["bids"]


def test_play_round_always_answers_something_valid() -> None:
    for text in ["", "null", "{}", "not json", None, 42, make_message(gold=None)]:
        answer = play_round(Brain(), text, "me")
        assert answer == {"bids": {}, "points_to_spend": 0}


def test_safe_sale_sells_nothing_when_the_sale_crashes() -> None:
    current_round = Round(9000, AUCTIONS, {}, BANK_STATE, points=20_000, gold_per_point=60.0)
    assert safe_sale(BrokenSeller(Settings(sell_share=0.05)), current_round) == 0


def test_a_crashing_sale_never_touches_the_bids() -> None:
    answer = play_round(BrokenSeller(Settings(sell_share=0.05)), make_message(points=20_000), "me")
    assert answer["points_to_spend"] == 0
    assert "a41" in answer["bids"]


def test_play_round_sells_only_when_selling_is_on() -> None:
    message = make_message(points=20_000)
    assert play_round(Brain(), message, "me")["points_to_spend"] == 0
    # prix du marché par défaut 20, la banque paie 60 : 3 fois notre prix
    answer = play_round(Brain(Settings(sell_share=0.01)), message, "me")
    assert answer["points_to_spend"] == 200
    assert "a41" in answer["bids"]


def make_message(gold: Any = 7200, points: int = 0) -> str:
    return json.dumps({
        "states": {"me": {"gold": gold, "points": points}},
        "gold_per_point": 60.0,
        "auctions": {"a41": {"die": 12, "num": 4, "bonus": 2}},
        "prev_auctions": {},
        "remainder_gold_income": [1000] * 500,
        "remainder_bank_interest": [1.05] * 500,
        "remainder_bank_limit": [5000] * 500,
    })
