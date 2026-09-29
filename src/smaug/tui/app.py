"""The monitor: my agent's live signals next to the game's scoreboard, with a few levers (think: the control tower)"""

import argparse
import os
import time
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DataTable, Sparkline, Static

from smaug.tui.controls import describe, nudge, read_instructions, with_pause, with_preset, write_instructions
from smaug.tui.panels import (
    agent_text,
    control_text,
    game_text,
    ranking_row,
    statusline_left,
    statusline_right,
    tabline,
)
from smaug.tui.sources import fetch_leaderboard, game_summary, read_agent
from smaug.tui.style import CSS


class MonitorApp(App):
    """Refreshes both panels every second; the only file it ever writes is logs/control.json"""

    TITLE = "Monitor"
    CSS = CSS
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("plus,equals_sign", "lever('margin', 1)", "margin up"),
        ("minus", "lever('margin', -1)", "margin down"),
        ("E", "lever('min_expected_value', 1)", "min EV up"),
        ("e", "lever('min_expected_value', -1)", "min EV down"),
        ("W", "lever('history_rounds', 1)", "window up"),
        ("w", "lever('history_rounds', -1)", "window down"),
        ("p", "pause", "pause or resume"),
        ("1", "preset('normal')", "normal"),
        ("2", "preset('mixed')", "mixed class"),
        ("3", "preset('v1')", "first version"),
        ("0", "reset", "factory settings"),
    ]
    ENABLE_COMMAND_PALETTE = False
    # le temps pour confirmer une pause en rappuyant sur p
    PAUSE_CONFIRM_SECONDS = 3.0

    def __init__(self, host: str, port: int, our_name: str, logs_folder: Path) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.our_name = our_name
        self.logs_folder = logs_folder
        self.control_path = logs_folder / "control.json"
        self.pause_armed_until = 0.0

    def compose(self) -> ComposeResult:
        yield Static(tabline(), id="tabline")
        with Horizontal(id="body"):
            with Vertical(id="agent-panel", classes="panel"):
                yield Static(id="agent")
                yield Static(id="control")
                yield Static("market price, last 120 rounds", classes="chart-label")
                yield Sparkline([], id="market")
                yield Static("gold, last 120 rounds", classes="chart-label")
                yield Sparkline([], id="gold")
            with Vertical(id="game-panel", classes="panel"):
                yield Static(id="game")
                yield DataTable(id="ranking", cursor_type="none", zebra_stripes=True)
        with Horizontal(id="statusline"):
            yield Static(id="statusline-left")
            yield Static(id="statusline-right")

    def on_mount(self) -> None:
        self.theme = "tokyo-night"
        agent_panel = self.query_one("#agent-panel")
        agent_panel.border_title = " my agent "
        game_panel = self.query_one("#game-panel")
        game_panel.border_title = " the game "
        game_panel.border_subtitle = f"{self.host}:{self.port}"
        table = self.query_one("#ranking", DataTable)
        table.add_columns("#", "agent", "grade", "points", "gold", "gain/round")
        self.show(None, None)
        self.refresh_panels()
        # au plus une lecture du classement par seconde
        self.set_interval(1.0, self.refresh_panels)

    @work(thread=True, exclusive=True)
    def refresh_panels(self) -> None:
        # dans un fil à part : un serveur lent ne fige jamais l'écran
        agent = read_agent(self.logs_folder)
        board = fetch_leaderboard(self.host, self.port)
        game = None
        if board is not None:
            game = game_summary(board, self.our_name)
        self.call_from_thread(self.show, agent, game)

    def show(self, agent: dict | None, game: dict | None) -> None:
        self.query_one("#agent", Static).update(agent_text(agent))
        self.show_control()
        # le journal lu, pour voir tout de suite si c'est bien celui de la partie en cours
        logbook_name = "no logbook yet"
        if agent is not None:
            logbook_name = agent.get("logbook_name", "")
        self.query_one("#agent-panel").border_subtitle = f" {logbook_name} "
        if agent is not None and len(agent["market_prices"]) > 0:
            self.query_one("#market", Sparkline).data = agent["market_prices"]
        if agent is not None and len(agent["golds"]) > 0:
            self.query_one("#gold", Sparkline).data = agent["golds"]

        self.query_one("#game", Static).update(game_text(game, self.our_name))
        table = self.query_one("#ranking", DataTable)
        table.clear()
        if game is not None:
            for player in game["players"]:
                table.add_row(*ranking_row(player, self.our_name))

        server = f"{self.host}:{self.port}"
        clock = time.strftime("%H:%M:%S")
        self.query_one("#statusline-left", Static).update(
            statusline_left(agent, game, self.our_name)
        )
        self.query_one("#statusline-right", Static).update(
            statusline_right(server, clock, game is not None)
        )

    def show_control(self) -> None:
        if self.control_path.exists():
            description = describe(read_instructions(self.control_path))
        else:
            description = "no file yet: factory settings"
        pause_armed = time.monotonic() < self.pause_armed_until
        self.query_one("#control", Static).update(control_text(description, pause_armed))

    def send(self, change: str, update) -> None:
        """Reads control.json, applies one change and writes it back whole"""
        instructions = read_instructions(self.control_path)
        if instructions is None:
            self.notify("control.json was unreadable, starting again from the factory settings", severity="warning")
            instructions = {}
        updated = update(instructions)
        if write_instructions(self.control_path, updated):
            self.notify(f"{change}: {describe(updated)}", title="sent to the agent")
        else:
            self.notify(f"could not write {self.control_path}", severity="error")
        self.show_control()

    def action_lever(self, lever: str, direction: int) -> None:
        def update(instructions: dict) -> dict:
            return nudge(instructions, lever, direction)

        self.send(lever.replace("_", " "), update)

    def action_preset(self, preset: str) -> None:
        def update(instructions: dict) -> dict:
            return with_preset(instructions, preset)

        self.send(f"preset {preset}", update)

    def action_reset(self) -> None:
        def update(instructions: dict) -> dict:
            return {}

        self.send("factory settings", update)

    def action_pause(self) -> None:
        instructions = read_instructions(self.control_path)
        paused = instructions is not None and instructions.get("pause") is True
        if paused:
            def resume(current: dict) -> dict:
                return with_pause(current, False)

            self.send("resume", resume)
            return
        # une pause gèle l'agent : on demande de rappuyer pour confirmer
        if time.monotonic() < self.pause_armed_until:
            self.pause_armed_until = 0.0

            def pause(current: dict) -> dict:
                return with_pause(current, True)

            self.send("pause", pause)
            return
        self.pause_armed_until = time.monotonic() + self.PAUSE_CONFIRM_SECONDS
        self.notify("press p again within 3 seconds to pause the agent", severity="warning")
        self.show_control()


def main() -> None:
    parser = argparse.ArgumentParser(prog="make monitor")
    parser.add_argument("--host", default=os.environ.get("AH_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=os.environ.get("AH_PORT", "8000"))
    parser.add_argument("--name", default=os.environ.get("AH_NAME", "Dylan"))
    parser.add_argument("--logs", default="logs")
    values = parser.parse_args()
    MonitorApp(values.host, values.port, values.name, Path(values.logs)).run()


if __name__ == "__main__":
    main()
