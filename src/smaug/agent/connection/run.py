"""Starts the agent for real and calls back while it is safe (think: the ignition key)"""

import asyncio
import sys
import time
from pathlib import Path

from smaug.agent.connection.guard import is_previous_game_over, may_connect
from smaug.agent.connection.leftover import clear_unless_kept, leftover_instructions
from smaug.agent.connection.reconnect import RETRY_DELAY_SECONDS, should_call_back
from smaug.agent.connection.safe_client import SafeClient
from smaug.agent.connection.settings import read_connection_settings
from smaug.agent.strategy.brain import Brain

HINTS = {
    "refused": "The server refused us: wrong token, game already started, or server full.",
    "unreachable": "Cannot reach the server yet, retrying.",
    "dropped": "The line dropped.",
    "game_over": "The game is over.",
}


def main() -> None:
    settings = read_connection_settings(sys.argv[1:])
    if not may_connect(is_previous_game_over(settings), input):
        print("Not connecting, the scoreboard stays as it is.")
        return

    # une consigne oubliée après une répétition ne doit pas jouer la vraie partie en silence
    control_path = Path("logs") / "control.json"
    if clear_unless_kept(control_path, leftover_instructions(control_path), input):
        print("Cleared logs/control.json, playing with the default settings.")

    # un seul cerveau et un seul journal pour toute la partie, même après une reconnexion
    # pas de préfixe "agent_" : c'est celui des logs du client du prof
    logbook_path = Path("logs") / f"logbook_{settings.name}_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"
    client = SafeClient(settings, Brain(), logbook_path, control_path)
    last_rounds_left = None
    last_message_at = None

    while True:
        print(f"Calling {settings.host}:{settings.port} as {settings.name}")
        report = asyncio.run(client.call())
        if report.rounds_left is not None:
            last_rounds_left = report.rounds_left
        if report.last_message_at is not None:
            last_message_at = report.last_message_at
        print(f"Call ended after {report.rounds_received} rounds. {HINTS[report.ended_because]}")

        if not should_call_back(report.ended_because, last_rounds_left, last_message_at, time.monotonic()):
            break
        time.sleep(RETRY_DELAY_SECONDS)
        # deuxième sécurité : si la partie s'est terminée entre-temps, rappeler effacerait le tableau
        if is_previous_game_over(settings) is True:
            print("The game ended in the meantime, not calling back.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopped.")
