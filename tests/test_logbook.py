"""The logbook writes valid lines and never crashes the caller"""

import json

from smaug.agent.logbook import open_logbook, write_round


def test_write_round_appends_one_json_line(tmp_path):
    logbook_path = tmp_path / "logbook_test.jsonl"
    logbook = open_logbook(logbook_path)

    write_round(logbook, round_number=1, gold=500, answer={"bids": {"a1": 20}, "points_to_spend": 0})
    logbook.close()

    lines = logbook_path.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry == {"round": 1, "gold": 500, "bids": {"a1": 20}, "points_to_spend": 0}


def test_write_round_never_raises_on_a_bad_answer(tmp_path):
    logbook_path = tmp_path / "logbook_test.jsonl"
    logbook = open_logbook(logbook_path)

    write_round(logbook, round_number=1, gold=500, answer="not a dict")

    logbook.close()
