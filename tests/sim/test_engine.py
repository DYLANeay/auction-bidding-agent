from typing import Any

from smaug.agent.strategy.brain import Brain
from smaug.sim.engine import play_game
from smaug.sim.players import OurAgent, Player
from smaug.sim.teacher_agents import random_single, random_walk, tiny_bid


class Spy(Player):
    """Counts how many times the engine asks for bids"""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.questions = 0

    def answer(self, text: str, agent_id: str) -> Any:
        self.questions += 1
        return {}


def make_players() -> list[Player]:
    return [OurAgent("Dylan", Brain()), tiny_bid("tiny"), random_single("single"), random_walk("walk")]


def test_a_game_goes_to_the_end() -> None:
    ranking = play_game(make_players, rounds=50, seed=1)
    assert len(ranking) == 4
    points = [line[0] for line in ranking]
    assert points == sorted(points, reverse=True)


def test_the_same_seed_replays_the_same_game() -> None:
    assert play_game(make_players, rounds=50, seed=7) == play_game(make_players, rounds=50, seed=7)


def test_the_phantom_round_is_never_asked() -> None:
    spy = Spy("spy")

    def spy_and_one_opponent() -> list[Player]:
        return [spy, tiny_bid("tiny")]

    play_game(spy_and_one_opponent, rounds=50, seed=1)
    assert spy.questions == 49


class Seller(Player):
    """Never bids, sells 10 points every round"""

    def answer(self, text: str, agent_id: str) -> Any:
        return {"bids": {}, "points_to_spend": 10}


def test_a_point_sale_is_settled_like_on_the_server() -> None:
    def seller_and_one_opponent() -> list[Player]:
        return [Seller("seller"), tiny_bid("tiny")]

    def quiet_and_one_opponent() -> list[Player]:
        return [Spy("quiet"), tiny_bid("tiny")]

    with_sale = {name: (points, gold) for points, gold, name in play_game(seller_and_one_opponent, rounds=50, seed=1)}
    without_sale = {name: (points, gold) for points, gold, name in play_game(quiet_and_one_opponent, rounds=50, seed=1)}
    # 0 point au départ : il descend jusqu'au plancher de -100 du serveur, et reçoit de l'or en échange
    assert with_sale["seller"][0] == -100
    assert with_sale["seller"][1] > without_sale["quiet"][1]
