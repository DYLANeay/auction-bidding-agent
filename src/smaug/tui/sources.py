"""Where the monitor gets its news: our agent's logbook and the public scoreboard (think: the control tower's radar)"""

import json
import time
from pathlib import Path
from urllib.request import urlopen

from dnd_auction_game.net import http_scheme, resolve_ssl

# fenêtre des signaux récents (taux de victoire, or perdu)
RECENT_ROUNDS = 20
# au-delà, l'agent ne répond plus ou la partie est finie
SILENCE_SECONDS = 5.0


def latest_logbook(logs_folder: Path) -> Path | None:
    """The most recently written logbook, if any"""
    newest = None
    newest_time = 0.0
    try:
        candidates = list(logs_folder.glob("logbook_*.jsonl"))
    except OSError:
        return None
    for path in candidates:
        try:
            modified = path.stat().st_mtime
        except OSError:
            continue
        if newest is None or modified > newest_time:
            newest = path
            newest_time = modified
    return newest


def read_entries(path: Path) -> list[dict]:
    """Every complete line of the logbook, skipping a half-written one"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    entries = []
    for line in text.splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            entries.append(entry)
    return entries


def number(entry: dict, key: str) -> float:
    value = entry.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)


def agent_summary(entries: list[dict], seconds_since_last_line: float) -> dict | None:
    """What the agent panel shows, computed from the logbook lines"""
    if len(entries) == 0:
        return None
    last = entries[-1]
    recent = entries[-RECENT_ROUNDS:]

    won_recent = 0
    lost_recent = 0
    gold_lost_recent = 0.0
    for entry in recent:
        won_recent += int(number(entry, "won"))
        lost_recent += int(number(entry, "lost"))
        gold_lost_recent += number(entry, "gold_lost")

    gold_lost_total = 0.0
    slowest_ms = 0.0
    for entry in entries:
        gold_lost_total += number(entry, "gold_lost")
        slowest_ms = max(slowest_ms, number(entry, "response_ms"))

    win_rate = None
    if won_recent + lost_recent > 0:
        win_rate = won_recent / (won_recent + lost_recent)

    bids = last.get("bids")
    if not isinstance(bids, dict):
        bids = {}
    bids_gold = 0.0
    for gold in bids.values():
        if isinstance(gold, (int, float)):
            bids_gold += gold

    market_prices = []
    golds = []
    for entry in entries[-120:]:
        market_prices.append(number(entry, "market_price"))
        golds.append(number(entry, "gold"))

    return {
        "rounds_logged": len(entries),
        "rounds_left": last.get("rounds_left"),
        "gold": last.get("gold"),
        "win_rate": win_rate,
        "won_recent": won_recent,
        "lost_recent": lost_recent,
        "gold_lost_recent": gold_lost_recent,
        "gold_lost_total": gold_lost_total,
        "market_price": number(last, "market_price"),
        "market_prices": market_prices,
        "golds": golds,
        "margin": number(last, "margin"),
        "min_expected_value": number(last, "min_expected_value"),
        "history_rounds": int(number(last, "history_rounds")),
        "paused": last.get("paused") is True,
        "bids_count": len(bids),
        "bids_gold": bids_gold,
        "response_ms": number(last, "response_ms"),
        "slowest_ms": slowest_ms,
        "silent": seconds_since_last_line > SILENCE_SECONDS,
        "seconds_since_last_line": seconds_since_last_line,
    }


def agent_summary_hint(agent: dict) -> str | None:
    """One suggestion from the signal to lever table, or None when all looks fine"""
    if agent["slowest_ms"] > 10:
        return "a response took over 10 ms: check the machine"
    # "not too early" : les signaux se stabilisent en une centaine de tours
    if agent["rounds_logged"] < 100:
        return "too early to judge, signals settle after about 100 rounds"
    bids = agent["won_recent"] + agent["lost_recent"]
    if agent["win_rate"] is None or bids < 10:
        return None
    if agent["win_rate"] < 0.5:
        return "most bids lose: consider raising the margin"
    if agent["win_rate"] > 0.95:
        return "almost every bid wins: we may be overpaying, consider lowering the margin"
    return None


def read_agent(logs_folder: Path) -> dict | None:
    path = latest_logbook(logs_folder)
    if path is None:
        return None
    try:
        age = time.time() - path.stat().st_mtime
    except OSError:
        return None
    agent = agent_summary(read_entries(path), age)
    if agent is not None:
        agent["logbook_name"] = path.name
    return agent


def fetch_leaderboard(host: str, port: int) -> dict | None:
    """The public scoreboard, read with a plain GET: never a websocket, which could reset a finished game"""
    scheme = http_scheme(resolve_ssl(host, None))
    url = f"{scheme}://{host}:{port}/api/leadboard"
    try:
        with urlopen(url, timeout=0.8) as response:
            board = json.loads(response.read())
    except Exception:  # noqa: BLE001
        return None
    if not isinstance(board, dict):
        return None
    return board


def game_summary(board: dict, our_name: str) -> dict:
    """What the game panel shows: the ranking and where we stand"""
    players = board.get("players")
    if not isinstance(players, list):
        players = []

    ranking = []
    our_rank = None
    for player in players:
        if not isinstance(player, dict):
            continue
        rank = len(ranking) + 1
        name = str(player.get("name", "?"))
        ranking.append(
            {
                "rank": rank,
                "name": name,
                "grade": str(player.get("grade", "?")),
                "points": number(player, "points"),
                "gold": number(player, "gold"),
                "gain_10": number(player, "avg_gain_10"),
            }
        )
        if name == our_name and our_rank is None:
            our_rank = rank

    bank = board.get("bank_state")
    if not isinstance(bank, dict):
        bank = {}

    return {
        "round": board.get("round"),
        "is_done": board.get("is_done") is True,
        "players": ranking,
        "our_rank": our_rank,
        "gold_per_point": number(board, "gold_per_point"),
        "salary": number(bank, "gold_income_per_round"),
        "interest": number(bank, "bank_interest_per_round"),
        "bank_limit": number(bank, "bank_limit_per_round"),
    }
