"""Reusable maze generator, solver, and ASCII/color renderer.

This module contains the standalone ``MazeGenerator`` class used by the
``a_maze_ing.py`` CLI. It has no dependency on ``sys.argv`` or any other
CLI concern, so it can be imported and driven programmatically from other
projects (see README.md for a usage walkthrough).
"""

import random
import sys
import time
from collections import deque


class ConfigError(Exception):
    """Exception raised when the maze configuration is invalid.

    Raised whenever the configuration file is missing required keys,
    contains malformed values, or describes a maze that cannot be
    generated (e.g. out-of-bounds entry/exit coordinates).
    """

    def __init__(self, message: str = "Configuration Error") -> None:
        """Initialize the exception with a descriptive message.

        Args:
            message: Human-readable description of the configuration
                error. Defaults to "Configuration Error".
        """
        super().__init__(message)


class MazeGenerator():
    """Generates, solves, and serializes a maze from a configuration file.

    The maze is represented internally as a bird's-eye view mapping each
    cell's coordinates to a 4-bit wall bitmask (1=North, 2=East, 4=South,
    8=West). Cells are grouped into disjoint sets keyed by an integer
    cell number; merging two sets by breaking the wall between them is
    how the maze is carved.
    """

    def __init__(self) -> None:
        """Initialize an empty maze generator with no configuration loaded."""
        self._birdview_16: dict[tuple[int, int], int] = {}
        self._cell: dict[int, list[tuple[int, int]]] = {}
        self._width: int
        self._height: int
        self._entry: tuple[int, int]
        self._exit: tuple[int, int]
        self._forty_two: list[tuple[int, int]]
        self._outputfile: str
        self._is_perfect: bool
        self._ans: list[str] = []
        self._seed: int | None
        self._show_path: bool = True
        self._wall_color: int = 47
        self._display_mode: str = "color"

    @property
    def width(self) -> int:
        """The maze's width in cells, as loaded by :meth:`set_config`."""
        return self._width

    @property
    def height(self) -> int:
        """The maze's height in cells, as loaded by :meth:`set_config`."""
        return self._height

    @property
    def entry(self) -> tuple[int, int]:
        """The entry cell's ``(x, y)`` coordinates."""
        return self._entry

    @property
    def exit(self) -> tuple[int, int]:
        """The exit cell's ``(x, y)`` coordinates."""
        return self._exit

    @property
    def walls(self) -> dict[tuple[int, int], int]:
        """Bird's-eye view of the maze: ``(x, y)`` -> wall bitmask.

        Bit 0=North, 1=East, 2=South, 3=West; a set bit means that wall
        is closed. Populated by :meth:`set_view_default` and carved by
        the generation loop (:meth:`break_wall` / :meth:`manage_cell_num`).
        """
        return self._birdview_16

    @property
    def solution(self) -> list[str]:
        """Shortest entry-to-exit path as a list of ``N``/``E``/``S``/``W``
        direction letters, computed by :meth:`solve_bfs`."""
        return self._ans

    def set_config(self, path: str | None = None) -> None:
        """Load and validate the maze configuration from a file.

        Reads ``path`` (or, if omitted, the first command-line argument),
        parses it as ``KEY=VALUE`` lines, and populates the width,
        height, entry, exit, output file, and perfect-maze attributes.
        ``WIDTH``, ``HEIGHT``, ``ENTRY``, ``EXIT``, ``OUTPUT_FILE`` and
        ``PERFECT`` are mandatory; ``SEED`` is optional.

        Args:
            path: Path to the configuration file. Defaults to
                ``sys.argv[1]`` when not given, so the CLI can call
                ``set_config()`` with no arguments.

        Raises:
            ConfigError: If the file is missing a mandatory key, has an
                unknown or duplicate key, or if the width, height,
                entry, or exit values are invalid or out of bounds.
        """
        if path is None:
            if len(sys.argv) < 2:
                raise ConfigError(
                    "No config file specified. Pass a path to "
                    "set_config() or run: python3 a_maze_ing.py "
                    "<config_file>."
                )
            path = sys.argv[1]
        configs: dict[str, str] = {}
        try:
            with open(path) as fd:
                raw_configs: list[str] = fd.readlines()
        except OSError as e:
            raise ConfigError(
                f"Could not open config file '{path}': "
                f"{e.strerror}. Check the path and file permissions."
            )
        except UnicodeDecodeError:
            raise ConfigError(
                f"Config file '{path}' is not valid UTF-8 text. Save "
                f"it as plain UTF-8 text and try again."
            )
        raw_configs = [
            line for line in raw_configs
            if not (line.strip().startswith("#") or line == "\n")
        ]
        mandatory_keys: set[str] = {
            "WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE",
        }
        if len(raw_configs) < 6 or len(raw_configs) > 7:
            raise ConfigError(
                f"Config file must have 6 or 7 key=value lines, found "
                f"{len(raw_configs)}. Add the missing key(s) or remove "
                f"the extra/duplicate line(s) so that WIDTH, HEIGHT, "
                f"ENTRY, EXIT, PERFECT and OUTPUT_FILE each appear "
                f"once, with SEED appearing at most once."
            )
        for raw_line in raw_configs:
            stripped: str = raw_line.rstrip("\n")
            key_value: list[str] = stripped.split("=")
            if len(key_value) != 2:
                raise ConfigError(
                    f"Malformed line '{stripped}'. Each line must be "
                    f"in KEY=VALUE format with exactly one '='."
                )
            configs[key_value[0].upper()] = key_value[1]
        if len(configs.keys()) != len(raw_configs):
            raise ConfigError(
                "Config file has a duplicate key. Make sure each of "
                "WIDTH, HEIGHT, ENTRY, EXIT, PERFECT and OUTPUT_FILE "
                "appears exactly once, with SEED appearing at most "
                "once."
            )
        missing_keys: set[str] = mandatory_keys - configs.keys()
        if missing_keys:
            raise ConfigError(
                f"Config file is missing required key(s): "
                f"{', '.join(sorted(missing_keys))}."
            )
        for config_key in configs.keys():
            if config_key not in mandatory_keys | {"SEED"}:
                raise ConfigError(
                    f"Unknown config key '{config_key}'. Allowed keys "
                    f"are WIDTH, HEIGHT, ENTRY, EXIT, PERFECT, "
                    f"OUTPUT_FILE, SEED. Rename or remove '{config_key}'."
                )
        try:
            self._width = int(configs["WIDTH"])
        except ValueError:
            raise ConfigError(
                f"WIDTH value '{configs['WIDTH']}' is not a valid "
                f"positive integer. Set WIDTH to a positive whole number."
            )
        if self._width < 2:
            raise ConfigError(
                f"WIDTH={self._width} is too small. Set WIDTH to a "
                f"positive integer of 2 or greater."
            )
        try:
            self._height = int(configs["HEIGHT"])
        except ValueError:
            raise ConfigError(
                f"HEIGHT value '{configs['HEIGHT']}' is not a valid "
                f"positive integer. Set HEIGHT to a positive whole number."
            )
        if self._height < 2:
            raise ConfigError(
                f"HEIGHT={self._height} is too small. Set HEIGHT to a "
                f"positive integer of 2 or greater."
            )
        self._forty_two = self._compute_forty_two()
        self._entry = self._parse_coordinate(configs["ENTRY"], "ENTRY")
        self._validate_in_grid(self._entry, "ENTRY")
        self._exit = self._parse_coordinate(configs["EXIT"], "EXIT")
        self._validate_in_grid(self._exit, "EXIT")
        if self._entry == self._exit:
            raise ConfigError(
                f"ENTRY and EXIT are both {self._entry}. Choose two "
                f"different coordinates."
            )
        self._outputfile = configs["OUTPUT_FILE"]
        if configs["PERFECT"] not in ("True", "False"):
            raise ConfigError(
                f"PERFECT value '{configs['PERFECT']}' is invalid. Set "
                f"PERFECT to 'True' or 'False'."
            )
        self._is_perfect = configs["PERFECT"].capitalize() == "True"
        seed_value: str = configs.get("SEED", "")
        if seed_value != "":
            try:
                self._seed = int(seed_value)
            except ValueError:
                raise ConfigError(
                    f"SEED value '{seed_value}' is not a valid "
                    f"integer. Leave SEED empty or set it to a whole "
                    f"number."
                )
        else:
            self._seed = None
        random.seed(self._seed)

    def _parse_coordinate(self, raw: str, label: str) -> tuple[int, int]:
        """Parse an "x,y" string into a coordinate tuple.

        Args:
            raw: The raw "x,y" text to parse.
            label: Human-readable name of the field, used in error
                messages (e.g. "ENTRY").

        Returns:
            The parsed ``(x, y)`` coordinate.

        Raises:
            ConfigError: If ``raw`` is not two comma-separated integers.
        """
        parts: list[str] = raw.split(",")
        if len(parts) != 2:
            raise ConfigError(
                f"{label} '{raw}' must be in x,y format (e.g. '3,4')."
            )
        try:
            return int(parts[0]), int(parts[1])
        except ValueError:
            raise ConfigError(
                f"{label} '{raw}' must contain two integers separated "
                f"by a comma (e.g. '3,4')."
            )

    def _validate_in_grid(self, coord: tuple[int, int], label: str) -> None:
        """Check that a coordinate lies inside the grid and outside "42".

        Args:
            coord: The ``(x, y)`` coordinate to validate.
            label: Human-readable name of the field, used in error
                messages (e.g. "ENTRY").

        Raises:
            ConfigError: If ``coord`` is outside the grid or falls
                inside the reserved "42" pattern.
        """
        if (
                coord[0] < 0 or self._width <= coord[0]
                or coord[1] < 0 or self._height <= coord[1]
        ):
            raise ConfigError(
                f"{label} {coord} is outside the {self._width}x"
                f"{self._height} grid. Use 0 <= x < WIDTH and "
                f"0 <= y < HEIGHT."
            )
        if coord in self._forty_two:
            raise ConfigError(
                f"{label} {coord} falls inside the reserved '42' "
                f"pattern. Choose a different {label} coordinate."
            )

    def _compute_forty_two(self) -> list[tuple[int, int]]:
        """Compute the "42" pattern's cell coordinates for the current
        width and height.

        Builds the pattern centered on the grid, then falls back to no
        pattern at all if the grid is too small to contain it or if
        including it would split the remaining cells into more than
        one connected region (see :meth:`_forty_two_leaves_connected`).

        Returns:
            The "42" pattern's cell coordinates, or an empty list if
            the pattern cannot be placed for the current grid size.
        """
        if self._width < 7 or self._height < 5:
            return []
        mid_x: int = self._width // 2
        mid_y: int = self._height // 2
        candidate: list[tuple[int, int]] = [
            (mid_x - 3, mid_y - 2),
            (mid_x + 1, mid_y - 2),
            (mid_x + 2, mid_y - 2),
            (mid_x + 3, mid_y - 2),
            (mid_x - 3, mid_y - 1),
            (mid_x + 3, mid_y - 1),
            (mid_x - 3, mid_y),
            (mid_x - 2, mid_y),
            (mid_x - 1, mid_y),
            (mid_x + 1, mid_y),
            (mid_x + 2, mid_y),
            (mid_x + 3, mid_y),
            (mid_x - 1, mid_y + 1),
            (mid_x + 1, mid_y + 1),
            (mid_x - 1, mid_y + 2),
            (mid_x + 1, mid_y + 2),
            (mid_x + 2, mid_y + 2),
            (mid_x + 3, mid_y + 2),
        ]
        if self._forty_two_leaves_connected(candidate):
            return candidate
        return []

    def _forty_two_leaves_connected(
        self, candidate: list[tuple[int, int]]
    ) -> bool:
        """Check whether removing the candidate "42" cells still leaves
        every other cell reachable from every other via 4-directional
        moves.

        The carving algorithm merges cell groups only across a shared
        wall between adjacent cells, so if removing the "42" cells
        splits the remaining grid into more than one disconnected
        region, no sequence of wall-breaks can ever merge them into a
        single maze and :meth:`entry_point` would loop forever.

        Args:
            candidate: Coordinates of the candidate "42" pattern cells.

        Returns:
            True if the non-"42" cells form one connected region.
        """
        remaining: set[tuple[int, int]] = {
            (x, y)
            for y in range(self._height)
            for x in range(self._width)
            if (x, y) not in candidate
        }
        if not remaining:
            return False
        start: tuple[int, int] = next(iter(remaining))
        seen: set[tuple[int, int]] = {start}
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for neighbor in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if neighbor in remaining and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        return seen == remaining

    def set_view_default(self) -> None:
        """Initialize the bird's-eye view and per-cell grouping.

        Resets ``self._birdview_16`` and ``self._cell`` (so leftover
        state from a previous, differently-sized maze can never
        survive a regeneration), then sets every cell's wall bitmask
        to fully closed (15) and creates one singleton group per cell.
        When the "42" pattern was kept by :meth:`set_config` (or
        :meth:`entry_point`'s size-change menu), its cells are
        excluded from ``self._cell`` so they remain permanently
        isolated (fully closed) in the final maze. Otherwise the "42"
        pattern is omitted and a message is printed to the console.
        """
        self._birdview_16 = {}
        self._cell = {}
        if self._forty_two:
            for y in range(self._height):
                for x in range(self._width):
                    self._birdview_16[x, y] = 15
                    if (x, y) not in self._forty_two:
                        self._cell[y * self._width + x] = [(x, y)]
        else:
            print(
                f"Maze size {self._width}x{self._height} cannot fit a "
                f"connected '42' pattern; omitting it."
            )
            for y in range(self._height):
                for x in range(self._width):
                    self._birdview_16[x, y] = 15
                    self._cell[y * self._width + x] = [(x, y)]

    def fetch_random_cell_num(self) -> int:
        """Pick a random cell group key from the current cell groups.

        Returns:
            A key of ``self._cell`` chosen uniformly at random.
        """
        return random.choice(list(self._cell.keys()))

    def _open_wall(self, cell: tuple[int, int], bit: int) -> None:
        """Clear a single wall bit for the given cell, if it is set.

        Args:
            cell: Coordinates of the cell whose wall should be opened.
            bit: Bitmask of the wall to clear (1=North, 2=East, 4=South,
                8=West).
        """
        if self._birdview_16[cell] & bit:
            self._birdview_16[cell] = self._birdview_16[cell] - bit

    def horz_break(
        self, cells: tuple[tuple[int, int], tuple[int, int]]
    ) -> None:
        """Open the shared wall between two horizontally adjacent cells.

        Args:
            cells: A ``(coordinate1, coordinate2)`` tuple, where
                ``coordinate1`` and ``coordinate2`` are horizontally
                adjacent (differ only in x).
        """
        cell1: tuple[int, int] = cells[0]
        cell2: tuple[int, int] = cells[1]
        if cell1[0] < cell2[0]:
            self._open_wall(cell1, 2)
            self._open_wall(cell2, 8)
        else:
            self._open_wall(cell1, 8)
            self._open_wall(cell2, 2)

    def vert_break(
        self, cells: tuple[tuple[int, int], tuple[int, int]]
    ) -> None:
        """Open the shared wall between two vertically adjacent cells.

        Args:
            cells: A ``(coordinate1, coordinate2)`` tuple, where
                ``coordinate1`` and ``coordinate2`` are vertically
                adjacent (differ only in y).
        """
        cell1: tuple[int, int] = cells[0]
        cell2: tuple[int, int] = cells[1]
        if cell1[1] < cell2[1]:
            self._open_wall(cell1, 4)
            self._open_wall(cell2, 1)
        else:
            self._open_wall(cell1, 1)
            self._open_wall(cell2, 4)

    def fetch_cell_num(self, cell: tuple[int, int]) -> int:
        """Find the cell group key that a given coordinate belongs to.

        Args:
            cell: Coordinates to look up.

        Returns:
            The key of ``self._cell`` whose group contains ``cell``.

        Raises:
            KeyError: If ``cell`` does not belong to any group.
        """
        for num in self._cell.keys():
            if cell in self._cell[num]:
                return num
        raise KeyError(f"Cell {cell} does not belong to any group")

    def break_wall(self, cell1_num: int) -> tuple[int, int]:
        """Open a wall from a random cell in one group into a neighboring
        group.

        Repeatedly picks a random cell belonging to ``cell1_num`` until it
        finds one with a neighboring cell (excluding out-of-grid and "42"
        pattern coordinates) that belongs to a different group, opens the
        shared wall between them, and returns that neighbor.

        Args:
            cell1_num: Key of the cell group to carve outward from.

        Returns:
            The coordinates of the neighboring cell whose wall was opened.
        """
        while True:
            cell: tuple[int, int] = random.choice(self._cell[cell1_num])
            x: int = cell[0]
            y: int = cell[1]
            around_candidates: set[tuple[int, int]] = {
                (x+1, y), (x, y+1), (x-1, y), (x, y-1)
            }
            for neighbor in around_candidates:
                if neighbor not in self._birdview_16.keys():
                    continue
                if neighbor in self._forty_two:
                    continue
                cell2_num: int = self.fetch_cell_num(neighbor)
                if cell[0] == neighbor[0]:
                    if cell[1] + 1 == neighbor[1]:
                        if cell1_num != cell2_num:
                            wall_pair = (cell, neighbor)
                            self.vert_break(wall_pair)
                            return neighbor
                    if cell[1] - 1 == neighbor[1]:
                        if cell1_num != cell2_num:
                            wall_pair = (cell, neighbor)
                            self.vert_break(wall_pair)
                            return neighbor
                if cell[1] == neighbor[1]:
                    if cell[0] + 1 == neighbor[0]:
                        if cell1_num != cell2_num:
                            wall_pair = (cell, neighbor)
                            self.horz_break(wall_pair)
                            return neighbor
                    if cell[0] - 1 == neighbor[0]:
                        if cell1_num != cell2_num:
                            wall_pair = (cell, neighbor)
                            self.horz_break(wall_pair)
                            return neighbor

    def manage_cell_num(self, key1: int, key2: int) -> None:
        """Merge two cell groups into one after their wall has been opened.

        The coordinates of the group with the larger key are moved into
        the group with the smaller key, and the larger key is removed
        from ``self._cell``.

        Args:
            key1: Key of the first cell group.
            key2: Key of the second cell group.
        """
        if key1 < key2:
            self._cell[key1].extend(self._cell[key2])
            del self._cell[key2]
        else:
            self._cell[key2].extend(self._cell[key1])
            del self._cell[key1]

    def is_a_maze(self) -> bool:
        """Check whether all cells have been merged into a single group.

        Returns:
            True if exactly one cell group remains in ``self._cell``,
            meaning the maze carving is complete; False otherwise.
        """
        if len(self._cell) == 1:
            return True
        else:
            return False

    def save_a_maze(self) -> None:
        """Serialize the maze to the configured output file and stdout.

        Writes the hexadecimal wall grid, followed by a blank line, the
        entry coordinates, the exit coordinates, and the solution path
        computed by :meth:`solve_bfs`. The same content is printed to
        stdout. Errors encountered while writing the output file are
        caught and printed rather than raised.
        """
        output: str = ""
        for y in range(self._height):
            for x in range(self._width):
                output = output+format(self._birdview_16[(x, y)], "X")
            output = output+"\n"
        output = output+"\n"
        output = output+f"{self._entry[0]},{self._entry[1]}\n"
        output = output+f"{self._exit[0]},{self._exit[1]}\n"
        output = output+f"{''.join(self._ans)}\n"
        try:
            with open(self._outputfile, "w") as fd:
                fd.write(output)
        except OSError as e:
            print(e)

    def _path_coordinates(self) -> set[tuple[int, int]]:
        """Walk ``self._ans`` from the entry to compute visited cells.

        Returns:
            The set of coordinates crossed by the entry-to-exit solution
            path, including the entry cell itself.
        """
        moves: dict[str, tuple[int, int]] = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }
        current: tuple[int, int] = self._entry
        path: set[tuple[int, int]] = {current}
        for letter in self._ans:
            dx, dy = moves[letter]
            current = (current[0] + dx, current[1] + dy)
            path.add(current)
        return path

    def display(self, show_path: bool = True) -> None:
        """Print a plain-text ASCII rendering of the maze to stdout.

        Draws each cell's walls with ``+``, ``-``, and ``|`` characters,
        marking the entry as ``E``, the exit as ``X``, and, when
        requested, the solution path as ``.``.

        Args:
            show_path: Whether to mark the entry-to-exit solution path.
                Defaults to True.
        """
        path: set[tuple[int, int]] = (
            self._path_coordinates() if show_path else set()
        )
        lines: list[str] = []
        for y in range(self._height):
            top: str = ""
            mid: str = ""
            for x in range(self._width):
                top += "+"
                top += "---" if self._birdview_16[(x, y)] & 1 else "   "
                mid += "|" if self._birdview_16[(x, y)] & 8 else " "
                if (x, y) == self._entry:
                    marker: str = "E"
                elif (x, y) == self._exit:
                    marker = "X"
                elif (x, y) in path:
                    marker = "."
                else:
                    marker = " "
                mid += f" {marker} "
            top += "+"
            mid += "|" if self._birdview_16[
                (self._width - 1, y)] & 2 else " "
            lines.append(top)
            lines.append(mid)
        bottom: str = ""
        for x in range(self._width):
            bottom += "+"
            bottom += "---" if self._birdview_16[
                (x, self._height - 1)] & 4 else "   "
        bottom += "+"
        lines.append(bottom)
        print("\n".join(lines))

    def display_color(
        self,
        show_path: bool = False,
        wall_color: int = 47,
    ) -> None:
        """Print an ANSI-colored block rendering of the maze to stdout.

        Renders the maze on a 2x scale grid so that both cells and walls
        occupy their own row/column, using ANSI background-color escape
        codes for walls, open floor, entry, exit, closed ("42") cells,
        and the solution path.

        Args:
            show_path: Whether to highlight the entry-to-exit solution
                path. Defaults to False.
            wall_color: ANSI background color code used for walls.
                Defaults to 47 (white).
        """
        path: set[tuple[int, int]] = (
            self._path_coordinates() if show_path else set()
        )
        block: str = "  "
        rows: int = 2 * self._height + 1
        cols: int = 2 * self._width + 1
        lines: list[str] = []
        for r in range(rows):
            line: str = ""
            for c in range(cols):
                color: int = self._block_color(r, c, path, wall_color)
                line += f"\033[{color}m{block}"
            line += "\033[0m"
            lines.append(line)
        print("\n".join(lines))

    def _block_color(
        self,
        r: int,
        c: int,
        path: set[tuple[int, int]],
        wall_color: int,
    ) -> int:
        """Determine the ANSI background color for one block of the grid
        used by :meth:`display_color`.

        The 2x-scaled grid alternates between cell blocks (odd row, odd
        column), wall-intersection blocks (even row, even column), and
        wall-segment blocks (exactly one of row/column even) — this
        method dispatches on that parity to decide which color applies.

        Args:
            r: Row index in the 2x-scaled rendering grid.
            c: Column index in the 2x-scaled rendering grid.
            path: Coordinates on the entry-to-exit solution path, as
                returned by :meth:`_path_coordinates`.
            wall_color: ANSI background color code used for closed walls.

        Returns:
            The ANSI background color code for the block at ``(r, c)``.
        """
        black: int = 40
        if r % 2 == 1 and c % 2 == 1:
            x: int = (c - 1) // 2
            y: int = (r - 1) // 2
            if (x, y) == self._entry:
                return 45
            if (x, y) == self._exit:
                return 41
            if self._birdview_16[(x, y)] == 15:
                return 100
            if (x, y) in path:
                return 46
            return black
        if r % 2 == 0 and c % 2 == 0:
            return wall_color
        if r % 2 == 0:
            x = (c - 1) // 2
            y_below: int = r // 2
            if y_below == 0:
                closed: bool = bool(self._birdview_16[(x, 0)] & 1)
            elif y_below == self._height:
                closed = bool(self._birdview_16[(x, self._height - 1)] & 4)
            else:
                closed = bool(self._birdview_16[(x, y_below)] & 1)
            return wall_color if closed else black
        y = (r - 1) // 2
        x_right: int = c // 2
        if x_right == 0:
            closed = bool(self._birdview_16[(0, y)] & 8)
        elif x_right == self._width:
            closed = bool(self._birdview_16[(self._width - 1, y)] & 2)
        else:
            closed = bool(self._birdview_16[(x_right, y)] & 8)
        return wall_color if closed else black

    def solve_bfs(self) -> None:
        """Compute the shortest path from entry
        to exit via breadth-first search.

        Explores the maze from ``self._entry`` following open walls and
        records, for each visited cell, the direction letter used to
        reach it. The resulting path is stored as a list of direction
        letters (``N``, ``E``, ``S``, ``W``) in ``self._ans``.

        Raises:
            ConfigError: If the exit is unreachable from the entry.
        """
        # 1=N, 2=E, 4=S, 8=W
        directions: dict[int, tuple[str, tuple[int, int]]] = {
            1: ("N", (0, -1)),
            2: ("E", (1, 0)),
            4: ("S", (0, 1)),
            8: ("W", (-1, 0)),
        }

        queue: deque[tuple[int, int]] = deque([self._entry])
        visited: set[tuple[int, int]] = {self._entry}
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        while queue:
            current: tuple[int, int] = queue.popleft()
            if current == self._exit:
                break
            walls: int = self._birdview_16[current]
            for bit, (letter, (dx, dy)) in directions.items():
                if walls & bit:
                    continue
                neighbor: tuple[int, int] = (current[0] + dx, current[1] + dy)
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = (current, letter)
                    queue.append(neighbor)

        if self._exit != self._entry and self._exit not in came_from:
            raise ConfigError(
                f"EXIT {self._exit} is unreachable from ENTRY "
                f"{self._entry}. Move ENTRY/EXIT away from the "
                f"reserved '42' area or regenerate the maze."
            )

        node: tuple[int, int] = self._exit
        while node != self._entry:
            previous, letter = came_from[node]
            self._ans.append(letter)
            node = previous
        self._ans.reverse()

    def open_four_corner(self) -> None:
        """Break both interior walls of each of the four corner cells.

        Skips any break that :meth:`space_check` would reject, i.e. one
        that would complete a 3x3-or-larger open room (this can happen
        in narrow/short mazes where a corner's 3x3 window is otherwise
        already fully open).
        """
        corners: list[
            tuple[tuple[int, int], tuple[int, int], tuple[int, int]]
        ] = [
            ((0, 0), (1, 0), (0, 1)),
            (
                (self._width - 1, 0),
                (self._width - 2, 0),
                (self._width - 1, 1),
            ),
            (
                (0, self._height - 1),
                (1, self._height - 1),
                (0, self._height - 2),
            ),
            (
                (self._width - 1, self._height - 1),
                (self._width - 2, self._height - 1),
                (self._width - 1, self._height - 2),
            ),
        ]
        for corner, horz_neighbor, vert_neighbor in corners:
            if self.space_check(corner, horz_neighbor):
                self.horz_break((corner, horz_neighbor))
            if self.space_check(corner, vert_neighbor):
                self.vert_break((corner, vert_neighbor))

    def open_centre(self) -> None:
        """Break the centre cell's north/south walls into a corridor.

        The "42" pattern (when present) is always drawn with its
        horizontal strokes passing directly through the centre's east
        and west neighbors, but leaves the vertical gap between the "4"
        and the "2" clear above and below the centre. North/south is
        therefore the axis guaranteed to produce a real through-corridor
        rather than a dead end.

        Skips any break that :meth:`space_check` would reject, i.e. one
        that would complete a 3x3-or-larger open room.
        """
        ctr_x: int = self._width // 2
        ctr_y: int = self._height // 2
        centre: tuple[int, int] = (ctr_x, ctr_y)
        for neighbor in ((ctr_x, ctr_y + 1), (ctr_x, ctr_y - 1)):
            if (
                neighbor not in self._birdview_16
                or neighbor in self._forty_two
            ):
                continue
            if not self.space_check(centre, neighbor):
                continue
            self.vert_break((centre, neighbor))

    def find_dead_end(self) -> list[tuple[int, int]]:
        """Find every cell that has only one wall open.

        Returns:
            Coordinates of all non-"42" cells with exactly three closed
            walls (i.e. exactly one way in or out).
        """
        dead_ends: list[tuple[int, int]] = []
        for y in range(self._height):
            for x in range(self._width):
                xy: tuple[int, int] = (x, y)
                if xy in self._forty_two:
                    continue
                if bin(self._birdview_16[xy]).count("1") == 3:
                    dead_ends.append(xy)
        return dead_ends

    def _block_open_except(
        self,
        anchor: tuple[int, int],
        size: int,
        edge: tuple[tuple[int, int], tuple[int, int]],
    ) -> bool:
        """Check whether a size-by-size block is fully open, ignoring one edge.

        Args:
            anchor: Top-left coordinate of the block to inspect.
            size: Side length of the (square) block.
            edge: The one internal wall to disregard while checking,
                given as its two adjacent cells (order doesn't matter).

        Returns:
            True if every in-grid, non-"42" internal wall of the block
            other than ``edge`` is already open; False otherwise (which
            includes the block spilling outside the grid or into the
            "42" pattern, since that can never be a real open room).
        """
        cells: list[tuple[int, int]] = [
            (anchor[0] + i, anchor[1] + j)
            for i in range(size) for j in range(size)
        ]
        if any(
            c not in self._birdview_16 or c in self._forty_two
            for c in cells
        ):
            return False
        for i in range(size):
            for j in range(size - 1):
                a: tuple[int, int] = (anchor[0] + i, anchor[1] + j)
                b: tuple[int, int] = (anchor[0] + i, anchor[1] + j + 1)
                if {a, b} == set(edge):
                    continue
                if self._birdview_16[a] & 4:
                    return False
        for j in range(size):
            for i in range(size - 1):
                a = (anchor[0] + i, anchor[1] + j)
                b = (anchor[0] + i + 1, anchor[1] + j)
                if {a, b} == set(edge):
                    continue
                if self._birdview_16[a] & 2:
                    return False
        return True

    def space_check(
        self, xy: tuple[int, int], pair: tuple[int, int]
    ) -> bool:
        """Check whether breaking the wall between two cells stays legal.

        The maze may not contain a fully-open block 3 cells or wider in
        both dimensions. This checks every 3x3 window that would have
        the ``xy``-``pair`` wall as an internal edge, and rejects the
        break if any such window's other internal walls are already all
        open (i.e. breaking this one would complete an oversized room).

        Args:
            xy: One of the two cells sharing the wall to break.
            pair: The other cell sharing that wall (must be
                4-directionally adjacent to ``xy``).

        Returns:
            False if breaking the wall would complete a 3x3 (or larger)
            open block; True otherwise.
        """
        dx: int = pair[0] - xy[0]
        anchors: list[tuple[int, int]] = []
        if dx != 0:
            min_x: int = min(xy[0], pair[0])
            for x0 in (min_x - 1, min_x):
                for y0 in (xy[1] - 2, xy[1] - 1, xy[1]):
                    anchors.append((x0, y0))
        else:
            min_y: int = min(xy[1], pair[1])
            for y0 in (min_y - 1, min_y):
                for x0 in (xy[0] - 2, xy[0] - 1, xy[0]):
                    anchors.append((x0, y0))
        return not any(
            self._block_open_except(anchor, 3, (xy, pair))
            for anchor in anchors
        )

    def make_imperfect_maze(self) -> None:
        """Open the corners/centre, then knock down dead ends.

        Repeatedly finds every cell with a single opening and breaks one
        of its other closed walls (skipping grid edges, "42" cells, and
        breaks that would carve into an already-open block per
        :meth:`space_check`), stopping once a full pass makes no change.
        """
        self.open_four_corner()
        self.open_centre()
        directions: dict[int, tuple[int, int]] = {
            1: (0, -1), 2: (1, 0), 4: (0, 1), 8: (-1, 0),
        }
        while True:
            dead_ends: list[tuple[int, int]] = self.find_dead_end()
            if not dead_ends:
                break
            changed: bool = False
            for xy in dead_ends:
                status: int = self._birdview_16[xy]
                closed_walls: list[int] = [
                    wall for wall in (1, 2, 4, 8) if status & wall
                ]
                random.shuffle(closed_walls)
                for wall in closed_walls:
                    dx, dy = directions[wall]
                    pair: tuple[int, int] = (xy[0] + dx, xy[1] + dy)
                    if pair in self._forty_two:
                        continue
                    if (
                        pair[0] < 0 or self._width <= pair[0]
                        or pair[1] < 0 or self._height <= pair[1]
                    ):
                        continue
                    if not self.space_check(xy, pair):
                        continue
                    if wall in (1, 4):
                        self.vert_break((xy, pair))
                    else:
                        self.horz_break((xy, pair))
                    changed = True
                    break
            if not changed:
                break

    def _render(self) -> None:
        """Redraw the maze using the currently selected display mode."""
        if self._display_mode == "ascii":
            self.display(self._show_path)
        else:
            self.display_color(self._show_path, self._wall_color)

    def _generate_and_save(
        self, animate: bool = False, delay: float = 0.03
    ) -> None:
        """Carve a fresh maze, solve it, and write it to the output file.

        Repeatedly merges random adjacent cell groups until the whole
        grid (minus the "42" pattern) forms one connected maze, then
        computes the entry-to-exit solution and persists everything via
        :meth:`save_a_maze`. When ``PERFECT`` is false, the corners and
        centre are opened and dead ends are knocked down afterward (see
        :meth:`make_imperfect_maze`), and the solution is recomputed.

        Args:
            animate: Whether to redraw the maze after every wall-break,
                so the carving process is visible step by step.
            delay: Seconds to pause between animation frames. Ignored
                when ``animate`` is False.
        """
        self._ans = []
        self.set_view_default()
        while True:
            cell1_num: int = self.fetch_random_cell_num()
            cell2_num: int = self.fetch_cell_num(self.break_wall(cell1_num))
            self.manage_cell_num(cell1_num, cell2_num)
            if animate:
                print("\033[H\033[J", end="")
                self._render()
                time.sleep(delay)
            if self.is_a_maze():
                break
        self.solve_bfs()
        if not self._is_perfect:
            self.make_imperfect_maze()
            self._ans = []
            self.solve_bfs()
        self.save_a_maze()

    def entry_point(self) -> None:
        """Generate the initial maze, display it, and run the CLI menu.

        Carves and displays a maze from the already-loaded configuration,
        then loops over an interactive menu offering: re-generating a
        maze (optionally with a chosen seed, size, entry/exit, or
        perfect/imperfect setting), toggling the solution path display,
        rotating the wall color, switching between ASCII and color
        display, watching the carving process animate, and quitting.
        Runs until the user chooses to quit.
        """
        try:
            self._generate_and_save()
            self._render()
        except Exception as e:
            print(e)
        while True:
            print("=== A-Maze-ing ===")
            print("1. Re-generate a new maze")
            print("2. Re-generate with a specific seed")
            print("3. Change maze size (width/height)")
            print("4. Change entry/exit coordinates")
            print("5. Toggle PERFECT / imperfect")
            print("6. Show/Hide path from entry to exit")
            print("7. Rotate maze colors")
            print("8. Toggle ASCII / Color display")
            print("9. Play generation animation")
            print("10. Quit")
            choice: str = input("Choice? (1-10): ")
            if choice == "1":
                try:
                    self._generate_and_save()
                    self._render()
                except Exception as e:
                    print(e)
            elif choice == "2":
                raw_seed: str = input(
                    "New SEED (blank for random): "
                ).strip()
                try:
                    self._seed = int(raw_seed) if raw_seed != "" else None
                    random.seed(self._seed)
                    self._generate_and_save()
                    self._render()
                except ValueError:
                    print(f"SEED '{raw_seed}' is not a valid integer.")
                except Exception as e:
                    print(e)
            elif choice == "3":
                try:
                    new_width: int = int(input("New WIDTH: "))
                    new_height: int = int(input("New HEIGHT: "))
                    if new_width < 2 or new_height < 2:
                        raise ConfigError(
                            "WIDTH and HEIGHT must each be a positive "
                            "integer of 2 or greater."
                        )
                    self._width = new_width
                    self._height = new_height
                    self._forty_two = self._compute_forty_two()
                    try:
                        self._validate_in_grid(self._entry, "ENTRY")
                        self._validate_in_grid(self._exit, "EXIT")
                    except ConfigError:
                        self._entry = (0, 0)
                        self._exit = (self._width - 1, self._height - 1)
                        print(
                            "ENTRY/EXIT no longer fit the new size; "
                            f"reset to {self._entry} and {self._exit}."
                        )
                    self._generate_and_save()
                    self._render()
                except ValueError:
                    print("WIDTH and HEIGHT must be positive integers.")
                except Exception as e:
                    print(e)
            elif choice == "4":
                if not self._birdview_16:
                    print("No maze yet. Generate one first (option 1).")
                else:
                    try:
                        new_entry: tuple[int, int] = self._parse_coordinate(
                            input("New ENTRY (x,y): ").strip(), "ENTRY"
                        )
                        new_exit: tuple[int, int] = self._parse_coordinate(
                            input("New EXIT (x,y): ").strip(), "EXIT"
                        )
                        self._validate_in_grid(new_entry, "ENTRY")
                        self._validate_in_grid(new_exit, "EXIT")
                        if new_entry == new_exit:
                            raise ConfigError(
                                f"ENTRY and EXIT are both {new_entry}. "
                                f"Choose two different coordinates."
                            )
                        self._entry = new_entry
                        self._exit = new_exit
                        self._ans = []
                        self.solve_bfs()
                        self.save_a_maze()
                        self._render()
                    except Exception as e:
                        print(e)
            elif choice == "5":
                self._is_perfect = not self._is_perfect
                try:
                    self._generate_and_save()
                    self._render()
                except Exception as e:
                    print(e)
            elif choice == "6":
                if not self._birdview_16:
                    print("No maze yet. Generate one first (option 1).")
                else:
                    self._show_path = not self._show_path
                    self._render()
            elif choice == "7":
                if not self._birdview_16:
                    print("No maze yet. Generate one first (option 1).")
                else:
                    palette: list[int] = [47, 42, 43, 44, 46, 107, 100]
                    idx: int = (
                        palette.index(self._wall_color)
                        if self._wall_color in palette else 0
                    )
                    self._wall_color = palette[(idx + 1) % len(palette)]
                    self._render()
            elif choice == "8":
                if not self._birdview_16:
                    print("No maze yet. Generate one first (option 1).")
                else:
                    self._display_mode = (
                        "ascii" if self._display_mode == "color"
                        else "color"
                    )
                    self._render()
            elif choice == "9":
                try:
                    self._generate_and_save(animate=True)
                    self._render()
                except Exception as e:
                    print(e)
            elif choice == "10":
                return
