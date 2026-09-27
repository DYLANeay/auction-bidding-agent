"""The logbook writes valid lines, holds what the monitor needs and never crashes the caller"""

import json

from smaug.agent.config import Settings
from smaug.agent.logbook import open_logbook, round_entry, write_round
from smaug.agent.safety.game_round import Round
from smaug.agent.strategy.brain import Brain


def a_round() -> Round:
    prev_auctions = {
        "won": {"die": 6, "num": 2, "bonus": 0, "bids": [{"a_id": "me", "gold": 100}]},
        "lost": {"die": 6, "num": 2, "bonus": 0, "bids": [{"a_id": "other", "gold": 90}, {"a_id": "me", "gold": 40}]},
    }
    bank_state = {
        "gold_income_per_round": [1000, 1000, 1000],
        "bank_interest_per_round": [1.05, 1.05, 1.05],
        "bank_limit_per_round": [5000, 5000, 5000],
    }
    return Round(gold=700, auctions={}, prev_auctions=prev_auctions, bank_state=bank_state)


def test_write_round_appends_one_json_line(tmp_path) -> None:
    logbook_path = tmp_path / "logbook_test.jsonl"
    logbook = open_logbook(logbook_path)

    write_round(logbook, {"round": 1, "gold": 500})
    logbook.close()

    lines = logbook_path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {"round": 1, "gold": 500}


def test_write_round_never_raises_on_something_not_json(tmp_path) -> None:
    logbook = open_logbook(tmp_path / "logbook_test.jsonl")

    write_round(logbook, {"round": object()})

    logbook.close()


def test_round_entry_holds_what_the_monitor_needs() -> None:
    brain = Brain(Settings(margin=0.5))
    brain.price_history = [20.0, 30.0]
    answer = {"bids": {"a1": 20}, "points_to_spend": 0}

    entry = round_entry(7, a_round(), answer, brain, paused=False, response_ms=0.4567, agent_id="me")

    assert entry["round"] == 7
    assert entry["gold"] == 700
    assert entry["rounds_left"] == 3
    assert entry["bids"] == {"a1": 20}
    assert entry["won"] == 1
    assert entry["lost"] == 1
    assert entry["gold_lost"] == 20
    assert entry["market_price"] == 25.0
    assert entry["margin"] == 0.5
    assert entry["paused"] is False
    assert entry["response_ms"] == 0.46
    json.dumps(entry)


def test_round_entry_survives_an_unreadable_round() -> None:
    entry = round_entry(1, None, {"bids": {}, "points_to_spend": 0}, Brain(), paused=True, response_ms=0.1, agent_id="me")

    assert entry["gold"] is None
    assert entry["rounds_left"] is None
    assert entry["won"] == 0
    assert entry["paused"] is True
