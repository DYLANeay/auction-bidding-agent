"""The monitor starts and shows a waiting screen when nothing is there yet"""

import asyncio
import json

from textual.widgets import DataTable, Static

from smaug.tui.app import MonitorApp
from smaug.tui.panels import agent_text, game_text
from smaug.tui.sources import agent_summary, game_summary


def test_the_monitor_waits_without_logbook_or_server(tmp_path) -> None:
    async def run() -> None:
        app = MonitorApp("localhost", 1, "Dylan", tmp_path)
        async with app.run_test() as pilot:
            await pilot.pause(0.5)
            agent_panel = str(app.query_one("#agent", Static).render())
            game_panel = str(app.query_one("#game", Static).render())
            assert "Waiting for a logbook" in agent_panel
            assert "unreachable" in game_panel
            assert app.query_one("#ranking", DataTable).row_count == 0

    asyncio.run(run())


def test_the_monitor_shows_the_agent_and_the_ranking(tmp_path) -> None:
    entry = {"round": 1, "gold": 1234, "bids": {}, "won": 3, "lost": 1, "paused": True, "rounds_left": 10}
    (tmp_path / "logbook_Dylan_1.jsonl").write_text(json.dumps(entry) + "\n")

    async def run() -> None:
        app = MonitorApp("localhost", 1, "Dylan", tmp_path)
        async with app.run_test() as pilot:
            await pilot.pause(0.5)
            agent_panel = str(app.query_one("#agent", Static).render())
            assert "PAUSED" in agent_panel
            assert "1234" in agent_panel
            assert "75%" in agent_panel

            board = {"round": 5, "players": [{"name": "[bold]tricky", "grade": "A", "points": 50}]}
            app.show(None, game_summary(board, "Dylan"))
            assert app.query_one("#ranking", DataTable).row_count == 1

    asyncio.run(run())


def test_panel_texts_never_fail_on_a_player_name_with_markup() -> None:
    game = game_summary({"players": [{"name": "[red]Dylan[/]", "grade": "C"}]}, "[red]Dylan[/]")
    panel = game_text(game, "[red]Dylan[/]").plain
    assert "#1 of 1" in panel
    assert "interest        ?" in panel
    agent = agent_summary([{"gold": 5}], seconds_since_last_line=0.0)
    assert "gold            5" in agent_text(agent).plain
