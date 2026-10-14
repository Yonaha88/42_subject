"""Entry point of Fly-in, a drone routing simulator.

Usage:
    python3 main.py <map_file> [--visual]

Without --visual, the program prints one line per turn with the moves of
that turn ("D1-roof1 D2-corridorA"). With --visual, it also shows the
state of every zone after each turn and a summary of the metrics.
"""
import sys

from map_parser import MapParser, ParseError
from pathfinder import NoPathError
from planner import Planner
from validator import ScheduleValidator
from visualizer import Visualizer

USAGE = "Usage: python3 main.py <map_file> [--visual]"


class CommandLine:
    """The arguments given to the program."""

    def __init__(self, arguments: list[str]) -> None:
        """Read the arguments (without the program name).

        Args:
            arguments: For example ["maps/easy/01_linear_path.txt"].

        Raises:
            ValueError: If there is not exactly one map file, or if an
                option is unknown.
        """
        options = [arg for arg in arguments if arg.startswith("--")]
        files = [arg for arg in arguments if not arg.startswith("--")]
        for option in options:
            if option != "--visual":
                raise ValueError(f"unknown option '{option}'")
        if len(files) != 1:
            raise ValueError(f"expected 1 map file, got {len(files)}")
        self.map_file = files[0]
        self.visual = "--visual" in options


def main() -> None:
    """Read the map file given on the command line and run the simulation.

    Raises:
        SystemExit: If the arguments are wrong, if the map file is
            invalid, or if the end zone cannot be reached (exit status 1).
    """
    try:
        command = CommandLine(sys.argv[1:])
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(1)
    try:
        network = MapParser().parse_file(command.map_file)
        schedule = Planner().plan(network)
    except (ParseError, NoPathError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    problems = ScheduleValidator().validate(network, schedule)
    if problems:
        print(f"Error: the plan breaks a rule: {problems[0]}",
              file=sys.stderr)
        sys.exit(1)
    visualizer = Visualizer(network, Visualizer.terminal_supports_color())
    if command.visual:
        lines = visualizer.visual_lines(schedule)
    else:
        lines = visualizer.lines(schedule)
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
