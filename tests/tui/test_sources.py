"""The monitor reads the logbook and the scoreboard without ever crashing on missing or broken data"""

import json
import os

from smaug.tui.sources import (
    agent_summary,
    agent_summary_hint,
    fetch_leaderboard,
    game_summary,
    latest_logbook,
    read_agent,
    read_entries,
)


def line(**fields) -> dict:
    entry = {
        "round": 1,
        "gold": 1000,
        "bids": {"a1": 50, "a2": 30},
        "won": 1,
        "lost": 1,
        "gold_lost": 15,
        "market_price": 22.5,
        "margin": 0.3,
        "min_expected_value": 8.0,
        "history_rounds": 10,
        "paused": False,
        "rounds_left": 500,
        "response_ms": 0.2,
    }
    entry.update(fields)
    return entry


def test_latest_logbook_is_the_most_recent_one(tmp_path) -> None:
    old = tmp_path / "logbook_Dylan_1.jsonl"
    new = tmp_path / "logbook_Dylan_2.jsonl"
    old.write_text("")
    new.write_text("")
    os.utime(old, (1000, 1000))
    (tmp_path / "agent_teacher.jsonl").write_text("")
    assert latest_logbook(tmp_path) == new


def test_no_logbook_and_no_folder_give_nothing(tmp_path) -> None:
    assert latest_logbook(tmp_path) is None
    assert latest_logbook(tmp_path / "missing") is None


def test_read_entries_skips_a_half_written_line(tmp_path) -> None:
    path = tmp_path / "logbook_Dylan.jsonl"
    path.write_text(json.dumps(line()) + "\n" + '{"round": 2, "go')
    assert len(read_entries(path)) == 1
    assert read_entries(tmp_path / "missing.jsonl") == []


def test_agent_summary_counts_the_recent_signals() -> None:
    entries = [line(), line(won=3, lost=0, gold_lost=0), line(paused=True)]
    agent = agent_summary(entries, seconds_since_last_line=1.0)
    assert agent is not None
    assert agent["won_recent"] == 5
    assert agent["lost_recent"] == 2
    assert agent["win_rate"] == 5 / 7
    assert agent["gold_lost_total"] == 30
    assert agent["bids_count"] == 2
    assert agent["bids_gold"] == 80
    assert agent["paused"] is True
    assert agent["silent"] is False


def test_agent_summary_survives_junk_values() -> None:
    agent = agent_summary([{"won": "many", "bids": None, "margin": None}], seconds_since_last_line=60.0)
    assert agent is not None
    assert agent["win_rate"] is None
    assert agent["bids_count"] == 0
    assert agent["silent"] is True
    assert agent_summary([], seconds_since_last_line=0.0) is None


def test_hint_waits_before_suggesting_anything() -> None:
    entries = [line(won=0, lost=5)] * 50
    agent = agent_summary(entries, seconds_since_last_line=1.0)
    assert agent is not None
    assert "too early" in str(agent_summary_hint(agent))


def test_hint_suggests_a_higher_margin_when_most_bids_lose() -> None:
    entries = [line(won=1, lost=4)] * 150
    agent = agent_summary(entries, seconds_since_last_line=1.0)
    assert agent is not None
    assert "raising the margin" in str(agent_summary_hint(agent))


def test_game_summary_finds_our_rank_and_skips_broken_players() -> None:
    board = {
        "round": 42,
        "is_done": False,
        "players": [
            {"name": "Smaug", "grade": "A", "points": 900, "gold": 10},
            "broken",
            {"name": "Dylan", "grade": "B", "points": "lots"},
        ],
        "bank_state": {"gold_income_per_round": 1000, "bank_interest_per_round": 1.05, "bank_limit_per_round": 5000},
        "gold_per_point": 21.5,
    }
    game = game_summary(board, "Dylan")
    assert game["round"] == 42
    assert game["our_rank"] == 2
    assert game["players"][1]["points"] == 0
    assert game["salary"] == 1000


def test_game_summary_of_an_empty_board() -> None:
    game = game_summary({}, "Dylan")
    assert game["players"] == []
    assert game["our_rank"] is None


def test_an_unreachable_scoreboard_gives_nothing() -> None:
    assert fetch_leaderboard("localhost", 1) is None


def test_read_agent_names_the_logbook_it_reads(tmp_path) -> None:
    (tmp_path / "logbook_Dylan_1.jsonl").write_text(json.dumps(line()) + "\n")
    agent = read_agent(tmp_path)
    assert agent is not None
    assert agent["logbook_name"] == "logbook_Dylan_1.jsonl"
