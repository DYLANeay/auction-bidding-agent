# shortcuts for the project, like the scripts in package.json

# reads the connection settings from .env if it exists
-include .env
export

.PHONY: install test check battle rehearsal sim tournament

install:  # python 3.12 and all dependencies into .venv
	uv sync --all-groups

test:  # run the tests
	uv run pytest -q

check: test  # run before every commit

battle:  # play for real, with sleep blocked and the settings from .env
	systemd-inhibit --what=idle:sleep --why="auction battle" uv run python -m smaug.agent.connection.run

rehearsal:  # full local game: make rehearsal ROUNDS=300 OPPONENTS=5
	scripts/local_game.sh $(or $(ROUNDS),300) $(or $(OPPONENTS),5)

sim:  # one simulated game in seconds: make sim CLASS=mixed ROUNDS=1000 SEED=1
	uv run python -m smaug.sim.run_one --class $(or $(CLASS),mixed) --rounds $(or $(ROUNDS),1000) --seed $(or $(SEED),1)

tournament:  # many simulated games per class and setting: make tournament GAMES=20 FIRST_SEED=1
	uv run python -m smaug.sim.tournament --games $(or $(GAMES),20) --first-seed $(or $(FIRST_SEED),1)
