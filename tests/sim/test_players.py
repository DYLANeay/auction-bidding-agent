import json
from typing import Any

import numpy as np

from smaug.agent.strategy.brain import Brain
from smaug.sim.players import OurAgent, Player, ask_player
from smaug.sim.teacher_agents import EXAMPLES, random_single, random_walk, tiny_bid


def make_message() -> str:
    return json.dumps({
        "round": 5,
        "states": {"me": {"gold": 7200, "points": 30}, "other": {"gold": 900, "points": 10}},
        "auctions": {"a41": {"die": 12, "num": 4, "bonus": 2}, "a42": {"die": 6, "num": 3, "bonus": 7}},
        "prev_auctions": {},
        "gold_per_point": 40.0,
        "remainder_gold_income": [1000] * 500,
        "remainder_bank_interest": [1.05] * 500,
        "remainder_bank_limit": [5000] * 500,
    })


class CrashingPlayer(Player):
    def answer(self, text: str, agent_id: str) -> Any:
        raise ValueError("bug")


class NumpyPlayer(Player):
    def answer(self, text: str, agent_id: str) -> Any:
        return {"bids": {"a41": np.int64(100)}}


def test_our_agent_answers_like_in_a_real_game() -> None:
    answer = ask_player(OurAgent("Dylan", Brain()), make_message(), "me")
    assert answer["points_to_spend"] == 0
    assert "a41" in answer["bids"]


def test_the_teacher_agents_answer_bids() -> None:
    for player in [tiny_bid("tiny"), random_single("single"), random_walk("walk")]:
        answer = ask_player(player, make_message(), "me")
        assert isinstance(answer["bids"], dict)


def test_a_crashing_player_bids_nothing_this_round() -> None:
    assert ask_player(CrashingPlayer("crasher"), make_message(), "me") == {}


def test_a_numpy_answer_does_not_count() -> None:
    assert ask_player(NumpyPlayer("numpy"), make_message(), "me") == {}


def test_borrowing_the_teacher_agents_writes_nothing_in_context() -> None:
    tiny_bid("tiny")
    random_walk("walk")
    assert not (EXAMPLES / "__pycache__").exists()
