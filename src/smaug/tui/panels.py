"""What each part of the monitor says, as colored text (think: the words on the control tower's screens)"""

from rich.text import Text

from smaug.tui.sources import agent_summary_hint
from smaug.tui.style import (
    BACKGROUND,
    BACKGROUND_DARK,
    BACKGROUND_HIGHLIGHT,
    BLUE,
    COMMENT,
    CYAN,
    FOREGROUND,
    FOREGROUND_DARK,
    GRADE_COLORS,
    GREEN,
    HINT,
    MAGENTA,
    MUTED,
    ORANGE,
    RED,
    SEPARATOR_LEFT,
    SEPARATOR_RIGHT,
    YELLOW,
)

KEY_WIDTH = 16
GAUGE_WIDTH = 20


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def heading(lines: Text, title: str, color: str) -> None:
    lines.append("▎", style=color)
    lines.append(f"{title}\n", style=f"bold {color}")


def row(lines: Text, key: str, value: str, value_style: str = FOREGROUND) -> None:
    lines.append(f"  {key.ljust(KEY_WIDTH)}", style=FOREGROUND_DARK)
    lines.append(f"{value}\n", style=value_style)


def gauge(share: float, color: str) -> Text:
    filled = round(max(0.0, min(1.0, share)) * GAUGE_WIDTH)
    bar = Text()
    bar.append("━" * filled, style=color)
    bar.append("━" * (GAUGE_WIDTH - filled), style=BACKGROUND_HIGHLIGHT)
    return bar


def win_rate_color(win_rate: float) -> str:
    if win_rate < 0.5:
        return RED
    if win_rate > 0.95:
        return YELLOW
    return GREEN


def agent_text(agent: dict | None) -> Text:
    if agent is None:
        return Text(
            "  Waiting for a logbook in logs/\n  start the agent with make battle or make rehearsal",
            style=COMMENT,
        )

    lines = Text()
    if agent["paused"]:
        lines.append("  PAUSED  no bids are sent \n\n", style=f"bold {BACKGROUND} on {RED}")
    if agent["silent"]:
        lines.append(
            f"  no new round for {agent['seconds_since_last_line']:.0f}s: agent stopped or game over\n\n",
            style=YELLOW,
        )

    heading(lines, "Round", BLUE)
    rounds = str(agent["rounds_logged"])
    if agent["rounds_left"] is not None:
        rounds += f"  ({agent['rounds_left']} left)"
    row(lines, "played", rounds)
    row(lines, "gold", str(agent["gold"]), YELLOW)
    row(lines, "bids now", f"{agent['bids_count']} for {agent['bids_gold']:.0f} gold")
    lines.append("\n")

    heading(lines, "Risk, last 20 rounds", MAGENTA)
    lines.append(f"  {'win rate'.ljust(KEY_WIDTH)}", style=FOREGROUND_DARK)
    if agent["win_rate"] is None:
        lines.append("no bids yet\n", style=COMMENT)
    else:
        color = win_rate_color(agent["win_rate"])
        lines.append(gauge(agent["win_rate"], color))
        lines.append(f" {percent(agent['win_rate'])}", style=f"bold {color}")
        lines.append(f"  ({agent['won_recent'] + agent['lost_recent']} bids)\n", style=COMMENT)
    row(lines, "gold lost", f"{agent['gold_lost_recent']:.0f}", RED)
    row(lines, "lost in total", f"{agent['gold_lost_total']:.0f}", COMMENT)
    lines.append("\n")

    heading(lines, "Market", CYAN)
    row(lines, "price", f"{agent['market_price']:.1f} gold per point", CYAN)
    response_color = GREEN
    if agent["slowest_ms"] > 10:
        response_color = RED
    row(lines, "response", f"{agent['response_ms']:.2f} ms  (slowest {agent['slowest_ms']:.2f})", response_color)
    lines.append("\n")

    heading(lines, "Settings", GREEN)
    row(lines, "margin", percent(agent["margin"]))
    row(lines, "min EV", f"{agent['min_expected_value']:g}")
    row(lines, "price window", f"{agent['history_rounds']} rounds")

    hint = agent_summary_hint(agent)
    if hint is not None:
        lines.append("\n")
        lines.append("  ● hint ", style=f"bold {HINT}")
        lines.append(f"{hint}\n", style=f"italic {HINT}")
    return lines


def game_text(game: dict | None, our_name: str) -> Text:
    if game is None:
        return Text("  Scoreboard unreachable, retrying every second", style=COMMENT)

    lines = Text()
    heading(lines, "Standing", MAGENTA)
    if game["our_rank"] is None:
        row(lines, our_name, "not on the scoreboard", YELLOW)
    else:
        ours = game["players"][game["our_rank"] - 1]
        lines.append(f"  {our_name.ljust(KEY_WIDTH)}", style=FOREGROUND_DARK)
        lines.append(f"#{game['our_rank']}", style=f"bold {BLUE}")
        lines.append(f" of {len(game['players'])}   grade ", style=FOREGROUND)
        lines.append(ours["grade"], style=GRADE_COLORS.get(ours["grade"], FOREGROUND))
        lines.append(f"   {ours['points']:.0f} points\n", style=FOREGROUND)
    lines.append("\n")

    heading(lines, "Bank", BLUE)
    row(lines, "salary", f"{game['salary']:.0f}", YELLOW)
    interest = "?"
    # un taux de 1.05 veut dire +5 %, 0 veut dire que le serveur ne l'a pas donné
    if game["interest"] > 0:
        interest = f"{(game['interest'] - 1) * 100:.1f}%  up to {game['bank_limit']:.0f} gold"
    row(lines, "interest", interest)
    row(lines, "last price", f"{game['gold_per_point']:.1f} gold per point (all winners)", CYAN)
    return lines


def ranking_row(player: dict, our_name: str) -> list[Text]:
    is_us = player["name"] == our_name
    name_style = FOREGROUND
    marker = "  "
    if is_us:
        name_style = f"bold {CYAN}"
        marker = "▶ "
    return [
        Text(str(player["rank"]), style=COMMENT, justify="right"),
        Text(marker + player["name"], style=name_style),
        Text(player["grade"], style=GRADE_COLORS.get(player["grade"], FOREGROUND), justify="center"),
        Text(f"{player['points']:.0f}", style=FOREGROUND, justify="right"),
        Text(f"{player['gold']:.0f}", style=YELLOW, justify="right"),
        Text(f"{player['gain_10']:.1f}", style=GREEN, justify="right"),
    ]


def mode(agent: dict | None, game: dict | None) -> tuple[str, str]:
    """The label and color of the mode block, like Neovim's NORMAL or INSERT"""
    if game is not None and game["is_done"]:
        return "GAME OVER", MAGENTA
    if agent is None:
        return "WAITING", MUTED
    if agent["paused"]:
        return "PAUSED", RED
    if agent["silent"]:
        return "IDLE", YELLOW
    return "LIVE", GREEN


def segment(line: Text, label: str, background: str, foreground: str, next_background: str, bold: bool = False) -> None:
    style = f"{foreground} on {background}"
    if bold:
        style = f"bold {style}"
    line.append(f" {label} ", style=style)
    line.append(SEPARATOR_RIGHT, style=f"{background} on {next_background}")


def statusline_left(agent: dict | None, game: dict | None, our_name: str) -> Text:
    label, color = mode(agent, game)
    line = Text()
    segment(line, label, color, BACKGROUND, BACKGROUND_HIGHLIGHT, bold=True)

    rounds = "no round yet"
    if game is not None and game["round"] is not None:
        rounds = f"round {game['round']}"
    if agent is not None and agent["rounds_left"] is not None:
        rounds += f" · {agent['rounds_left']} left"
    segment(line, rounds, BACKGROUND_HIGHLIGHT, BLUE, BACKGROUND_DARK)

    standing = our_name
    if game is not None and game["our_rank"] is not None:
        ours = game["players"][game["our_rank"] - 1]
        standing = f"{our_name}  #{game['our_rank']}  {ours['grade']}"
    line.append(f" {standing} ", style=f"{FOREGROUND_DARK} on {BACKGROUND_DARK}")
    return line


def statusline_right(server: str, clock: str, connected: bool) -> Text:
    line = Text()
    server_color = GREEN if connected else RED
    line.append(SEPARATOR_LEFT, style=f"{BACKGROUND_HIGHLIGHT} on {BACKGROUND_DARK}")
    line.append(" ● ", style=f"{server_color} on {BACKGROUND_HIGHLIGHT}")
    line.append(f"{server} ", style=f"{FOREGROUND_DARK} on {BACKGROUND_HIGHLIGHT}")
    line.append(SEPARATOR_LEFT, style=f"{BLUE} on {BACKGROUND_HIGHLIGHT}")
    line.append(f" {clock} ", style=f"bold {BACKGROUND} on {BLUE}")
    return line


KEYS = [
    ("+ -", "margin"),
    ("e E", "min EV"),
    ("w W", "window"),
    ("p", "pause"),
    ("1", "normal"),
    ("2", "mixed"),
    ("3", "v1"),
    ("0", "reset"),
    ("q", "quit"),
]


def tabline() -> Text:
    line = Text()
    segment(line, "SMAUG", BLUE, BACKGROUND, BACKGROUND_HIGHLIGHT, bold=True)
    segment(line, "monitor", BACKGROUND_HIGHLIGHT, BLUE, BACKGROUND_DARK)
    for key, label in KEYS:
        line.append(f"  {key}", style=f"bold {BLUE} on {BACKGROUND_DARK}")
        line.append(f" {label}", style=f"{COMMENT} on {BACKGROUND_DARK}")
    return line


def control_text(description: str, pause_armed: bool) -> Text:
    """What logs/control.json asks for right now"""
    lines = Text()
    heading(lines, "Control", ORANGE)
    row(lines, "control.json", description, ORANGE)
    if pause_armed:
        lines.append("  press p again to pause the agent\n", style=f"bold {BACKGROUND} on {YELLOW}")
    return lines
