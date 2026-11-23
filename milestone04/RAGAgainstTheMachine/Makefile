MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

.PHONY: install run debug clean lint lint-strict test serve

install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	rm -rf .mypy_cache .pytest_cache
	find . -path ./.venv -prune -o -name '__pycache__' -print0 \
		| xargs -0 rm -rf

lint:
	uv run flake8 .
	uv run mypy . $(MYPY_FLAGS)

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

test:
	uv run pytest -q

serve:
	uv run python -m src serve --port 8000
