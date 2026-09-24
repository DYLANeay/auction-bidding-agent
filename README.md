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

## Layout

```
src/smaug/   the code (agent, tui, sim, analysis)
tests/       the tests
context/     the teacher's game, read only
```
