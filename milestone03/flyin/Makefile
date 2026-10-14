PYTHON = uv run --quiet python3

MAP = maps/challenger/01_the_impossible_dream.txt

MYPY = uv run --quiet mypy

MYPY_FLAG = --warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

FLAKE8 = uv run --quiet flake8

FLAKE8_FLAG = --extend-exclude .venv

run:
	$(PYTHON) main.py $(MAP)

visual:
	$(PYTHON) main.py $(MAP) --visual

debug:
	$(PYTHON) -m pdb main.py $(MAP)

install:
	uv sync

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -name "__pycache__" | xargs rm -rf

lint:
	$(FLAKE8) . $(FLAKE8_FLAG)
	$(MYPY) . $(MYPY_FLAG)

lint-strict:
	$(FLAKE8) . $(FLAKE8_FLAG)
	$(MYPY) . --strict

.PHONY: install run visual debug clean lint lint-strict
