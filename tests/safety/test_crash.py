"""Thousands of random and broken server messages, the agent must survive them all (think: the crash test)"""

import json
import math
import random
import time
from typing import Any

from smaug.agent.safety.airbag import play_round
from smaug.agent.safety.incoming import bid_gold
from smaug.agent.strategy.brain import Brain

MESSAGES = 10_000
DIE_SIZES = [2, 3, 4, 6, 8, 10, 12, 20]
JUNK = [None, "", "abc", -1, -(10**12), 10**12, 0, 1.5, float("nan"), float("inf"), [], {}, [1, 2], {"x": 1}, True]


def random_auction(generator: random.Random) -> dict:
    return {
        "die": generator.choice(DIE_SIZES),
        "num": generator.randint(1, 10),
        "bonus": generator.randint(-10, 20),
    }


def random_message(generator: random.Random) -> dict:
    auctions = {}
    for number in range(30):
        auctions[f"a{number}"] = random_auction(generator)

    prev_auctions = {}
    for number in range(30):
        bids = []
        for player in range(generator.randint(0, 5)):
            bids.append({"a_id": f"p{player}", "gold": generator.randint(1, 3000)})
        bids.sort(key=bid_gold, reverse=True)
        result = random_auction(generator)
        result["bids"] = bids
        prev_auctions[f"b{number}"] = result

    rounds_left = generator.randint(1, 1000)
    return {
        "states": {"me": {"gold": generator.randint(0, 20000), "points": 0}},
        "auctions": auctions,
        "prev_auctions": prev_auctions,
        "remainder_gold_income": [1000] * rounds_left,
        "remainder_bank_interest": [1.05] * rounds_left,
        "remainder_bank_limit": [5000] * rounds_left,
    }


def break_message(generator: random.Random, message: dict) -> None:
    """Damages one random part of the message, the way a trapped server could"""
    damage = generator.randint(1, 7)
    if damage == 1:
        key = generator.choice(list(message))
        del message[key]
    elif damage == 2:
        key = generator.choice(list(message))
        message[key] = generator.choice(JUNK)
    elif damage == 3:
        auction = message["auctions"][generator.choice(list(message["auctions"]))]
        field = generator.choice(["die", "num", "bonus"])
        auction[field] = generator.choice(JUNK)
    elif damage == 4:
        result = message["prev_auctions"][generator.choice(list(message["prev_auctions"]))]
        result["bids"] = generator.choice([JUNK, [{"gold": "lots"}], "bids", [None, 5]])
    elif damage == 5:
        # mises dans le désordre : le prix du marché ne doit pas se tromper de gagnant
        for result in message["prev_auctions"].values():
            generator.shuffle(result["bids"])
    elif damage == 6:
        key = generator.choice(["remainder_gold_income", "remainder_bank_interest", "remainder_bank_limit"])
        values = message[key]
        values[generator.randrange(len(values))] = generator.choice(JUNK)
    else:
        message["states"]["me"]["gold"] = generator.choice(JUNK)


def gold_we_can_spend(message: Any) -> int | None:
    """What our gold really is in the message, if it is a usable number"""
    try:
        gold = message["states"]["me"]["gold"]
    except (KeyError, TypeError):
        return None
    if isinstance(gold, bool) or not isinstance(gold, (int, float)):
        return None
    if not math.isfinite(gold) or gold < 0:
        return None
    return int(gold)


def check_answer(answer: dict, gold: int | None) -> None:
    assert set(answer) == {"bids", "points_to_spend"}
    assert answer["points_to_spend"] == 0
    total = 0
    for auction_id, bid in answer["bids"].items():
        assert type(auction_id) is str
        assert type(bid) is int
        assert bid >= 1
        total += bid
    if gold is None:
        assert answer["bids"] == {}
    else:
        assert total <= gold
    # le piège numpy : la réponse doit toujours pouvoir partir en JSON
    json.dumps(answer)


def test_the_agent_survives_thousands_of_random_and_broken_messages() -> None:
    generator = random.Random(42)
    # un seul cerveau pour tous les messages, comme pendant une vraie partie
    brain = Brain()
    durations = []

    for _ in range(MESSAGES):
        roll = generator.random()
        if roll < 0.05:
            # du pur n'importe quoi à la place du message
            text: Any = generator.choice(["", "null", "{", "[1, 2]", "x" * 1000, "[" * 5000, 42, None])
            gold = None
        else:
            message = random_message(generator)
            if roll < 0.6:
                break_message(generator, message)
            gold = gold_we_can_spend(message)
            text = json.dumps(message)

        start = time.perf_counter()
        answer = play_round(brain, text, "me")
        durations.append(time.perf_counter() - start)

        check_answer(answer, gold)

    durations.sort()
    slowest_but_one_percent = durations[int(len(durations) * 0.99)]
    assert slowest_but_one_percent < 0.010
