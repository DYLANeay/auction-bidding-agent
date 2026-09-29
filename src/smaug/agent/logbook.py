"""Ship's logbook: writes one line per round so we can see what the agent decided, since the teacher's client never records it"""

import json
from pathlib import Path
from typing import TextIO

from smaug.agent.report import last_round_results
from smaug.agent.safety.game_round import Round
from smaug.agent.strategy.brain import Brain
from smaug.agent.strategy.market import market_price


def open_logbook(path: Path) -> TextIO:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("a", encoding="utf-8")


def round_entry(
    round_number: int,
    current_round: Round | None,
    answer: dict,
    brain: Brain,
    paused: bool,
    response_ms: float,
    agent_id: str,
) -> dict:
    """Everything the monitor needs about one round"""
    # tour illisible : on note quand même la ligne, avec des trous
    gold = None
    rounds_left = None
    results = {"won": 0, "lost": 0, "gold_lost": 0}
    if current_round is not None:
        gold = current_round.gold
        rounds_left = len(current_round.bank_state["gold_income_per_round"])
        results = last_round_results(current_round.prev_auctions, agent_id)

    settings = brain.settings
    price = market_price(brain.price_history, settings.default_price)
    return {
        "round": round_number,
        "gold": gold,
        "bids": answer.get("bids", {}),
        "points_to_spend": answer.get("points_to_spend", 0),
        "won": results["won"],
        "lost": results["lost"],
        "gold_lost": results["gold_lost"],
        "market_price": round(price, 2),
        "margin": settings.margin,
        "min_expected_value": settings.min_expected_value,
        "history_rounds": settings.history_rounds,
        "sell_share": settings.sell_share,
        "paused": paused,
        "rounds_left": rounds_left,
        "response_ms": round(response_ms, 2),
    }


def write_round(logbook: TextIO, entry: dict) -> None:
    try:
        logbook.write(json.dumps(entry) + "\n")
        logbook.flush()
    except Exception:  # noqa: BLE001
        pass
