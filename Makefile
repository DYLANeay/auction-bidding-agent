# shortcuts for the project, like the scripts in package.json

.PHONY: install test check

install:  # python 3.12 and all dependencies into .venv
	uv sync --all-groups

test:  # run the tests
	uv run pytest -q

check: test  # run before every commit
