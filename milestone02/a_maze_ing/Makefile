PYTHON		= python3
MAIN		= a_maze_ing.py
CONFIG		= config.txt
PACKAGE		= mazegen

.PHONY: install run debug clean lint lint-strict build

install:
	uv venv
	uv pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ .mypy_cache build dist *.egg-info

lint:
	.venv/bin/flake8 .
	.venv/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	.venv/bin/flake8 .
	.venv/bin/mypy . --strict

build:
	.venv/bin/python -m build
	rm -f $(PACKAGE)-*.whl $(PACKAGE)-*.tar.gz
	cp dist/$(PACKAGE)-*.whl dist/$(PACKAGE)-*.tar.gz .
