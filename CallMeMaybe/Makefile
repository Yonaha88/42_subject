PYTHON = uv run python3

MYPY = uv run mypy

MYPY_FLAG = --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

FLAKE8 = uv run flake8

run:
	$(PYTHON) -m src

debug:
	$(PYTHON) -m pdb -m src

install:
	uv sync

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -name "__pycache__" | xargs rm -rf

lint:
	$(FLAKE8) src
	$(MYPY) src $(MYPY_FLAG)

lint-strict:
	$(FLAKE8) src
	$(MYPY) src --strict

.PHONY: install run debug clean lint lint-strict
