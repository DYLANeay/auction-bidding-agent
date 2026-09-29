# Smaug auction agent

Bidding agent for the IKT110 auction house battle, built on
[dnd_auction_game](https://github.com/ooki/dnd_auction_game) 0.6.0.

## Setup

With [uv](https://docs.astral.sh/uv/) (recommended):

```bash
make install
```

With plain pip (Python 3.12):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e . pytest
```

## Commands

| Command        | What it does                          |
|----------------|---------------------------------------|
| `make install` | install Python 3.12 and dependencies  |
| `make test`    | run the tests                         |
| `make check`   | run before every commit               |
| `make battle`  | play for real, using the settings in `.env` |
| `make monitor` | live view of our agent and the scoreboard, in a second terminal |
| `make rehearsal` | full local game against the teacher's example agents (`ROUNDS=300 OPPONENTS=5`) |
| `make sim` | one simulated game in seconds, no server (`CLASS=weak\|mixed\|strong ROUNDS=1000 SEED=1`) |
| `make tournament` | many simulated games per class and setting, summary in `results/tournament.md` (`GAMES=20 FIRST_SEED=1`) |

## Play

Copy the example settings and fill in the values given by the teacher (`.env` is never committed):

```bash
cp .env.example .env
make battle
```

The agent waits for the game to start, plays every round and calls back after a drop while the game is still running. If the previous game is already over, it asks before connecting, because connecting would reset the scoreboard.

## Monitor

In a second terminal, while the agent plays:

```bash
make monitor
```

It shows my agent's signals from `logs/logbook_*.jsonl` (win rate, gold lost, market
price, active settings, pause, response time) next to the scoreboard read from
`/api/leadboard`. It never talks to the agent directly: its keys only write
`logs/control.json`, which the agent reads and bounds every round.

| Key | Effect |
|-----|--------|
| `+` `-` | margin up or down by 5 points |
| `E` `e` | min EV up or down by 1 |
| `W` `w` | price window up or down by 5 rounds |
| `s` | point selling off, or back on at the default setting |
| `p` | pause (press twice to confirm) or resume |
| `1` `2` `3` | presets: normal, mixed class, first version |
| `0` | back to the default settings |
| `q` | quit the monitor (the agent keeps playing) |

## Live control

The agent plays alone with its default settings. To adjust it during a game, without
restarting it, write `logs/control.json`; it is read every round:

```json
{"margin": 0.5, "min_expected_value": 2, "history_rounds": 10, "pause": false}
```

`"sell_share": 0` switches point selling off (at most 0.05, 5% of the points per round).
Every key is optional and every value is bounded. Remove a key, or write `{}`, to go back
to the defaults (deleting the file keeps the last instructions). `"pause": true` keeps the
agent connected but sends no bids.

At startup, `make battle` shows any instructions left in the file and clears them unless
you answer `y`, so a rehearsal never leaks into a real game.

## Layout

```
src/smaug/   the code (agent, tui, sim, analysis)
tests/       the tests
context/     the teacher's game, read only
```
