*This project has been created as part of the 42 curriculum by hkanamit, kyonaha.*

## Description

**A-Maze-ing** is a Python maze generator, solver, and terminal renderer built
for the 42 `a_maze_ing` project.

Given a plain-text configuration file, the program:

- Carves a random maze of the requested width/height, guaranteeing full
  connectivity between all non-excluded cells.
- Optionally forces the maze to be *perfect* (exactly one path between the
  entry and the exit) or, if not, adds at least one extra loop.
- Always leaves a visible, fully-closed **"42"** pattern of cells inside the
  maze (when the grid is large enough to fit it).
- Solves the maze from entry to exit with a breadth-first search and writes
  the result (wall grid, entry, exit, solution) to an output file in the
  format described in Chapter IV.5 of the subject.
- Renders the maze in the terminal, both as plain ASCII and as an
  ANSI-colored grid, and offers an interactive menu to regenerate the maze,
  toggle the solution path, and rotate the wall color.

The maze-generation, solving, and rendering logic is implemented as a single
reusable class, `MazeGenerator`, packaged separately from the CLI so it can
be dropped into other projects — see [Code Reusability](#code-reusability).

## Instructions

### Requirements

- Python >= 3.10 (see `pyproject.toml`). No third-party runtime dependencies.
- [`uv`](https://docs.astral.sh/uv/) is used by the `Makefile` to manage a
  local virtual environment for linting/building; it isn't required just to
  run the program.

### Running the maze generator

```sh
python3 a_maze_ing.py config.txt
# or, equivalently:
make run
```

`config.txt` is the only argument and can be replaced with the path to any
config file following the format described in
[Configuration File Format](#configuration-file-format). A default
`config.txt` is included at the repository root.

The program never crashes on bad input: invalid configuration, missing
files, syntax errors, or unfeasible maze parameters are all caught and
reported with a clear error message instead of a traceback.

### Development commands (`Makefile`)

| Command | Description |
|---|---|
| `make install` | Create a `.venv` (via `uv`) and install `flake8`, `mypy`, `build`. |
| `make run` | Run `a_maze_ing.py` against `config.txt`. |
| `make debug` | Run `a_maze_ing.py` under `pdb`. |
| `make lint` | Run `flake8` and `mypy` (relaxed rules). |
| `make lint-strict` | Run `flake8` and `mypy --strict`. |
| `make build` | Rebuild the `mazegen` package (`.whl` + `.tar.gz`) from source. |
| `make clean` | Remove caches and build artifacts. |

## Configuration File Format

Each non-empty, non-comment line of the config file must be a single
`KEY=VALUE` pair. Lines starting with `#` are treated as comments and
ignored.

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in cells (>= 2). | `WIDTH=10` |
| `HEIGHT` | Maze height in cells (>= 2). | `HEIGHT=10` |
| `ENTRY` | Entry coordinates `x,y`, inside the grid and outside the "42" pattern. | `ENTRY=0,0` |
| `EXIT` | Exit coordinates `x,y`, inside the grid, different from `ENTRY`, and outside the "42" pattern. | `EXIT=9,9` |
| `OUTPUT_FILE` | Name of the file the generated maze is written to. | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True` for exactly one entry-to-exit path, `False` to add an extra loop. | `PERFECT=True` |
| `SEED` | Optional; when set, makes the random maze reproducible. Leave empty for a random seed. | `SEED=42` |

`WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE`, and `PERFECT` are
mandatory; `SEED` is optional and may be omitted entirely or left empty.
Any deviation — a missing mandatory key, an unknown key, a duplicate key,
or an out-of-range value — raises a `ConfigError` with a descriptive
message rather than crashing the program.

## Maze Generation Algorithm

**A-Maze-ing** carves mazes with a **randomized, union-find–based variant of
Kruskal's algorithm**:

1. Every cell starts in its own singleton group (`self._cell`), except the
   cells that make up the "42" pattern, which are left out entirely so they
   stay permanently walled off.
2. A group is picked at random, then a random cell inside it is picked, and
   one of its neighbors belonging to a *different* group is found.
3. The wall between the two cells is opened and their groups are merged
   (union) via `manage_cell_num`.
4. This repeats until only one group remains, i.e. the maze is a single
   spanning tree connecting every non-"42" cell — a perfect maze.
5. If `PERFECT=False`, `make_imperfect_maze` turns that spanning tree into
   a Pac-Man-style board:
   - `open_four_corner` breaks both interior walls of each of the four
     corner cells, and `open_centre` breaks the centre cell's north/south
     walls into a corridor (north/south rather than east/west, since the
     "42" pattern always keeps that axis clear of its own cells).
   - It then repeatedly finds every dead end (a cell with only one open
     side) and knocks down one of its other walls, skipping any break
     that would complete a fully-open block 3 cells or wider in both
     dimensions (`space_check`), until a full pass removes none.

### Why this algorithm

- **Natural support for excluded cells.** The "42" pattern cells simply
  never get a group and are never considered as neighbors. A disjoint-set
  approach handles "holes" in the grid for free, whereas a
  recursive-backtracker (DFS-based) approach would need extra bookkeeping to
  avoid walking into (or getting stuck around) excluded cells.
- **No directional bias.** Recursive backtracking tends to produce long,
  winding corridors because it always carves from the most recently visited
  cell. Driving the carving from a randomly chosen *existing group* instead
  keeps growth spread across the whole grid, which pairs naturally with the
  "no corridor wider than 2 cells" requirement.
- **Simplicity.** Merging two groups (`manage_cell_num`) is just moving one
  group's cells into the other, and checking whether the maze is finished
  (`is_a_maze`) is just checking whether a single group remains — both are
  simple, cheap operations. Opening a wall (`horz_break`/`vert_break`) always
  clears the matching bit on both cells at once, so the two cells' walls can
  never disagree about whether a passage between them is open.

### Enforcing "no open area 3 cells or wider"

The base spanning-tree carve can never produce a fully-open 3x3+ block on
its own (a cycle-free tree can't spare the extra edge needed to fully open a
square block of cells), but the `PERFECT=False` braiding pass deliberately
adds extra loops and could open one up if left unchecked. Before every
braiding wall-break, `space_check` enumerates each 3x3 window that would
have that wall as an internal edge and checks whether every *other* internal
wall in that window is already open; if so, breaking this one would
complete a 3x3 (or larger) open room, so the break is skipped instead.

This is checked with `tests/test_maze_constraints.py` (run with
`python3 -m unittest tests/test_maze_constraints.py`), which generates
mazes at several sizes and seeds and scans every 3x3 window post-generation
for full openness, alongside checks for wall coherence, border closure,
dead-end counts, corner/centre openness, and `PERFECT=True` spanning-tree
correctness.

## Visual Representation & Advanced Features

- **ASCII rendering** (`display`): a plain `+ - |` line-art rendering of the
  maze, marking the entry (`E`), exit (`X`), and, if requested, the solution
  path (`.`).
- **ANSI color rendering** (`display_color`, used by the CLI): a 2x-scaled
  colored block grid distinguishing walls, open floor, entry, exit, "42"
  cells, and the solution path.
- **Interactive menu**, available after the first maze is generated:
  1. Re-generate a new maze.
  2. Show/hide the entry-to-exit solution path.
  3. Rotate the wall color through a fixed palette.
  4. Quit.

## Code Reusability

The maze generation, solving, and rendering logic is consolidated into a
single standalone module, `mazegen.py`, independent of the `a_maze_ing.py`
CLI, so it can be reused from other projects. It is packaged at the
repository root as `mazegen-1.0.0-py3-none-any.whl` /
`mazegen-1.0.0.tar.gz` (regeneratable from source via `make build`, based on
`pyproject.toml`), and can be installed with `pip install`.

### Instantiation and basic usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator()
gen.set_config("config.txt")   # loads WIDTH/HEIGHT/ENTRY/EXIT/OUTPUT_FILE/PERFECT/SEED
gen.set_view_default()

while True:
    cell1 = gen.fetch_random_cell_num()
    cell2 = gen.fetch_cell_num(gen.break_wall(cell1))
    gen.manage_cell_num(cell1, cell2)
    if gen.is_a_maze():
        break

gen.solve_bfs()
gen.display()  # render as ASCII in the terminal
```

### Passing custom parameters (size, seed, etc.)

Parameters are passed via the configuration file (format as described
[above](#configuration-file-format)). To use custom values for size, seed,
entry, exit, etc., pass a file containing those values to `set_config()`.

```python
gen = MazeGenerator()
gen.set_config("my_custom_config.txt")  # WIDTH=30, HEIGHT=20, SEED=42, ...
```

### Accessing the generated structure and solution

```python
gen.width, gen.height   # maze dimensions
gen.entry, gen.exit     # entry/exit coordinates
gen.walls                # dict[(x, y) -> int] wall bitmask, bird's-eye view
                          # (bit0=North, bit1=East, bit2=South, bit3=West)
gen.solution              # list[str] shortest entry-to-exit path, e.g. ["S", "E", "E"]
```

## Team & Project Management

### Contribution

- **hkanamit:** maze generation, config management, general parsing.
- **kyonaha:** maze solving, error management, `Makefile`, maze visualization.

### Planning

Kyonaha came up with the algorithm, and hkanamit implemented it in code. The
core approach never changed over the course of the project.

### Retrospective

- **What worked well:** the choice of algorithm.
- **What could be better:** supporting multiple algorithms.

### Tools used

`uv`, `flake8`, `mypy`.

## Resources

### References on maze generation

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) —
  overview of Kruskal's, Prim's, and recursive-backtracker approaches.
- Jamis Buck, [*Mazes for Programmers*](https://pragprog.com/titles/jbmaze/mazes-for-programmers/) and his
  ["Buckblog" maze algorithm series](https://weblog.jamisbuck.org/) — worked
  examples of the classic maze-carving algorithms, including randomized
  Kruskal's.
- Robert Sedgewick & Kevin Wayne, *Algorithms* (4th ed.), chapter on
  union-find — background for the disjoint-set structure this project's
  algorithm is built on.
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search) —
  background for the entry-to-exit solver (`solve_bfs`).

### AI usage

[Claude Code](https://claude.com/claude-code) (Anthropic) was used as a
coding assistant on this project for:

- Writing/completing the docstrings on the `MazeGenerator` and
  `ConfigError` classes in `mazegen.py`.
- Drafting and structuring this `README.md`.
- General code review and debugging support (verifying the CLI, the
  library usage example, and the packaged wheel/sdist all still work after
  the above changes).
- Drafting the `Makefile`.

All algorithm design, maze-validity rules, and prior implementation work are
the team's own.
