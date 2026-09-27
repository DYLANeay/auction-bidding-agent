# shortcuts for the project, like the scripts in package.json

# reads the connection settings from .env if it exists
-include .env
export

.PHONY: install test check battle

install:  # python 3.12 and all dependencies into .venv
	uv sync --all-groups

test:  # run the tests
	uv run pytest -q

check: test  # run before every commit

battle:  # play for real, with sleep blocked and the settings from .env
	systemd-inhibit --what=idle:sleep --why="auction battle" uv run python -m smaug.agent.connection.run
