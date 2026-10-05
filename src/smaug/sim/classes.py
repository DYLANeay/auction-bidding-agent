"""The classes we test against, built from what already exists (think: the classmates in the auction room)"""

import random
from dataclasses import replace

from smaug.agent.config import DEFAULT_SETTINGS, NO_SELLING_SETTINGS, Settings
from smaug.agent.strategy.brain import Brain
from smaug.sim.players import OurAgent, Player
from smaug.sim.teacher_agents import random_single, random_walk, tiny_bid

OUR_NAME = "Dylan"


# but : un des trois agents du prof qui misent, à tour de rôle
def teacher_agent(number: int) -> Player:
    name = f"teacher_{number}"
    if number % 3 == 0:
        return tiny_bid(name)
    if number % 3 == 1:
        return random_single(name)
    return random_walk(name)


# but : notre agent avec d'autres réglages, comme un élève qui a eu la même idée que nous
def clone(number: int) -> Player:
    # les clones ne vendent pas, comme lors du tournoi de la vente
    settings = replace(
        NO_SELLING_SETTINGS,
        margin=random.uniform(0, 0.5),
        reserve_factor=random.uniform(0, 1.5),
        history_rounds=random.randint(5, 50),
        min_expected_value=random.uniform(0, 8),
    )
    return OurAgent(f"clone_{number}", Brain(settings))


def weak_class(our_settings: Settings = DEFAULT_SETTINGS) -> list[Player]:
    players: list[Player] = [OurAgent(OUR_NAME, Brain(our_settings))]
    for number in range(19):
        players.append(teacher_agent(number))
    return players


def mixed_class(our_settings: Settings = DEFAULT_SETTINGS) -> list[Player]:
    players: list[Player] = [OurAgent(OUR_NAME, Brain(our_settings))]
    for number in range(10):
        players.append(teacher_agent(number))
    for number in range(9):
        players.append(clone(number))
    return players


def strong_class(our_settings: Settings = DEFAULT_SETTINGS) -> list[Player]:
    players: list[Player] = [OurAgent(OUR_NAME, Brain(our_settings))]
    for number in range(19):
        players.append(clone(number))
    return players


CLASSES = {"weak": weak_class, "mixed": mixed_class, "strong": strong_class}
