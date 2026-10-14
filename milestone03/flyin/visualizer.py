"""Colored terminal output of the simulation.

Two views are available:

- the normal output: the required "D<ID>-<zone>" lines, with every zone
  name painted in the color given in the map file;
- the visual mode (--visual): for every turn, the same line followed by
  the state of every zone (how full it is and which drones are inside),
  then a summary with the evaluation metrics.

Colors are only used when the output is a terminal and the NO_COLOR
environment variable is not set, so that the text stays clean when it is
saved to a file or read by another program.
"""
import os
import sys
from bisect import bisect_left, bisect_right

from models import Network, Zone, ZoneType
from schedule import Position, Schedule

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RAINBOW = (196, 208, 226, 46, 51, 33, 129)
MAX_LISTED = 10
GAUGE_SIZE = 10

COLOR_CODES: dict[str, int] = {
    "red": 196, "darkred": 88, "crimson": 161, "maroon": 52,
    "orange": 208, "gold": 220, "yellow": 226, "brown": 130,
    "green": 46, "lime": 118, "olive": 100, "teal": 30,
    "cyan": 51, "blue": 33, "navy": 18, "purple": 129,
    "violet": 177, "magenta": 201, "pink": 218, "indigo": 54,
    "white": 255, "silver": 250, "gray": 245, "grey": 245,
    "black": 240,
}


class Visualizer:
    """Paint the schedule for a terminal."""

    def __init__(self, network: Network, use_color: bool) -> None:
        """Prepare the visualizer.

        Args:
            network: The network being simulated.
            use_color: False to print plain text (no escape codes).
        """
        self._network = network
        self._use_color = use_color

    @staticmethod
    def terminal_supports_color() -> bool:
        """Tell if colors should be printed.

        Colors are used only when the output is a terminal and the
        NO_COLOR environment variable is not set (https://no-color.org).
        """
        return sys.stdout.isatty() and "NO_COLOR" not in os.environ

    def paint(self, text: str, color: str | None) -> str:
        """Color a text with a map color name.

        Args:
            text: The text to color.
            color: A color name from the map, or None.

        Returns:
            The text wrapped in ANSI escape codes, or unchanged when colors
            are off or the color name is unknown.
        """
        if not self._use_color or color is None:
            return text
        if color == "rainbow":
            return "".join(
                f"\033[38;5;{RAINBOW[index % len(RAINBOW)]}m{letter}"
                for index, letter in enumerate(text)
            ) + RESET
        code = COLOR_CODES.get(color.lower())
        if code is None:
            return text
        return f"\033[38;5;{code}m{text}{RESET}"

    def _style(self, text: str, style: str) -> str:
        """Make a text bold or dim when colors are on."""
        return f"{style}{text}{RESET}" if self._use_color else text

    def zone_name(self, zone_name: str) -> str:
        """Return a zone name painted in its own color."""
        return self.paint(zone_name, self._network.zones[zone_name].color)

    def move(self, number: int, position: Position) -> str:
        """Return one move, such as "D1-roof1", with colors.

        A drone flying toward a restricted zone shows the connection name
        in dim text: it is between two zones.
        """
        if position.in_transit:
            label = self._style(Schedule.label(self._network, position), DIM)
        else:
            label = self.zone_name(position.zone)
        return f"D{number}-{label}"

    def turn_line(self, schedule: Schedule, turn: int) -> str:
        """Return the output line of a turn, with colors."""
        return " ".join(self.move(number, position)
                        for number, position in schedule.changes(turn))

    def lines(self, schedule: Schedule) -> list[str]:
        """Return the normal output: one colored line per turn."""
        return [self.turn_line(schedule, turn)
                for turn in range(1, schedule.total_turns + 1)]

    def visual_lines(self, schedule: Schedule) -> list[str]:
        """Return the visual mode output: every turn with zone states.

        For each turn: the output line, then one row per zone that holds
        drones (a gauge of how full it is and the drones inside), the
        drones on a connection, and how many are delivered. A summary with
        the evaluation metrics ends the output.
        """
        inside_by_turn: dict[int, list[tuple[int, Position]]] = {}
        for number, timeline in enumerate(schedule.timelines, start=1):
            for turn, _, after in timeline.steps():
                if turn < timeline.arrival:
                    inside_by_turn.setdefault(turn, []).append(
                        (number, after)
                    )
        departures = sorted(t.departure for t in schedule.timelines)
        arrivals = sorted(t.arrival for t in schedule.timelines)
        total = len(schedule.timelines)
        output: list[str] = []
        for turn in range(0, schedule.total_turns + 1):
            title = "Turn 0 (start)" if turn == 0 else f"Turn {turn}"
            line = "" if turn == 0 else self.turn_line(schedule, turn)
            output.append(f"{self._style(title, BOLD)}  {line}".rstrip())
            waiting = total - bisect_left(departures, turn)
            delivered = bisect_right(arrivals, turn)
            output.extend(self._zone_rows(
                inside_by_turn.get(turn, []), waiting, delivered, total
            ))
            output.append("")
        output.extend(self.summary(schedule))
        return output

    def _zone_rows(
        self, inside: list[tuple[int, Position]], waiting: int,
        delivered: int, total: int,
    ) -> list[str]:
        """Describe where the drones are at the end of a turn.

        Args:
            inside: (drone number, position) of the drones that have left
                the start zone and are not delivered yet.
            waiting: How many drones have not left the start zone yet.
            delivered: How many drones are in the end zone.
            total: The number of drones.

        Returns:
            One row per zone that holds drones, then the drones in flight
            and the number of delivered drones.
        """
        in_zone: dict[str, list[int]] = {}
        flying: list[str] = []
        for number, position in inside:
            if position.in_transit:
                flying.append(f"D{number}->{self.zone_name(position.zone)}")
            else:
                in_zone.setdefault(position.zone, []).append(number)
        start = str(self._network.start)
        width = max(len(name) for name in self._network.zones)
        gauge_width = max(
            [len("(no limit)")]
            + [len(self._gauge(zone, zone.max_drones))
               for zone in self._network.zones.values()]
        )
        rows: list[str] = []
        for name, zone in self._network.zones.items():
            numbers = in_zone.get(name, [])
            count = len(numbers) + (waiting if name == start else 0)
            if count == 0 or name == self._network.end:
                continue
            padded = self.zone_name(name) + " " * (width - len(name))
            if name == start:
                gauge = "(no limit)".ljust(gauge_width)
                drones = f"{waiting} waiting" if waiting else ""
                if numbers:
                    drones += " " + self._listing(numbers)
            else:
                gauge = self._gauge(zone, count).ljust(gauge_width)
                drones = self._listing(numbers)
            kind = ""
            if zone.zone_type != ZoneType.NORMAL:
                kind = self._style(f" <{zone.zone_type.value}>", DIM)
            rows.append(f"  {padded} {gauge}{kind}  {drones.strip()}")
        if flying:
            shown = " ".join(flying[:MAX_LISTED])
            more = len(flying) - MAX_LISTED
            rows.append(f"  in flight: {shown}"
                        + (f" (+{more} more)" if more > 0 else ""))
        if delivered:
            rows.append(f"  delivered: {delivered}/{total}")
        return rows

    @staticmethod
    def _gauge(zone: Zone, count: int) -> str:
        """Draw how full a zone is, such as "[##.] 2/3".

        The bar is at most GAUGE_SIZE characters long, so zones with a very
        large capacity stay on one line.
        """
        size = min(zone.max_drones, GAUGE_SIZE)
        filled = min(size, -(-count * size // zone.max_drones))
        return ("[" + "#" * filled + "." * (size - filled)
                + f"] {count}/{zone.max_drones}")

    @staticmethod
    def _listing(numbers: list[int]) -> str:
        """List drone names, at most MAX_LISTED of them."""
        shown = " ".join(f"D{number}" for number in numbers[:MAX_LISTED])
        more = len(numbers) - MAX_LISTED
        return shown + (f" (+{more} more)" if more > 0 else "")

    def summary(self, schedule: Schedule) -> list[str]:
        """Return the evaluation metrics of the schedule.

        Returns:
            Total turns, average turns per drone, total path cost (the sum
            of the turns spent moving), and drones moved per turn.
        """
        drones = len(schedule.timelines)
        turns = schedule.total_turns
        arrivals = [timeline.arrival for timeline in schedule.timelines]
        moving = sum(len(schedule.changes(turn))
                     for turn in range(1, turns + 1))
        average = sum(arrivals) / drones if drones else 0.0
        per_turn = moving / turns if turns else 0.0
        return [
            self._style("Summary", BOLD),
            f"  drones delivered      : {drones}",
            f"  total turns           : {turns}",
            f"  average turns / drone : {average:.2f}",
            f"  total path cost       : {moving} turns of movement",
            f"  drones moved / turn   : {per_turn:.2f}",
        ]
