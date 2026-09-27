"""Ship's logbook: writes one line per round so we can see what the agent decided, since the teacher's client never records it"""

import json
from pathlib import Path
from typing import TextIO


def open_logbook(path: Path) -> TextIO:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("a", encoding="utf-8")


def write_round(logbook: TextIO, round_number: int, gold: int, answer: dict) -> None:
    try:
        line = {
            "round": round_number,
            "gold": gold,
            "bids": answer.get("bids", {}),
            "points_to_spend": answer.get("points_to_spend", 0),
        }
        logbook.write(json.dumps(line) + "\n")
        logbook.flush()
    except Exception:  # noqa: BLE001
        pass
