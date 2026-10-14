"""Where every drone is at each turn, and how to print it.

Turn 0 is the starting state: every drone is in the start zone. The
line printed for turn t lists the drones whose position changed between
turn t - 1 and turn t.
"""
from collections.abc import Iterator
from dataclasses import dataclass

from models import Connection, Network


@dataclass(frozen=True)
class Position:
    """Where one drone is at the end of a turn.

    Attributes:
        zone: The zone the drone is in or, while flying toward a
            restricted zone, the zone it is flying to.
        coming_from: While flying toward a restricted zone, the zone the
            drone left. None when the drone is in a zone.
    """

    zone: str
    coming_from: str | None = None

    @property
    def in_transit(self) -> bool:
        """True while the drone is on a connection."""
        return self.coming_from is not None


class Timeline:
    """The positions of one drone, turn after turn.

    A drone first waits in its origin (the start zone) until `departure`,
    then follows `path`. Only the path is stored, so a drone that waits
    for thousands of turns does not use thousands of list items.

    Attributes:
        origin: Where the drone is at turn 0 and until `departure`.
        departure: The last turn the drone spends in its origin before
            its first move.
        path: The positions at turns departure + 1, departure + 2, ...
            The last one is where the drone arrives.
    """

    def __init__(
        self, origin: Position, departure: int, path: list[Position],
    ) -> None:
        """Store the timeline.

        Args:
            origin: Position at turn 0.
            departure: Last turn spent in the origin before moving.
            path: Positions after the departure, one per turn.
        """
        self.origin = origin
        self.departure = departure
        self.path = path

    @classmethod
    def from_positions(cls, positions: list[Position]) -> "Timeline":
        """Build a timeline from one position per turn, from turn 0.

        Args:
            positions: For example [start, start, a, goal].

        Returns:
            The same timeline, with the waiting turns at the beginning
            folded into `departure`.
        """
        departure = 0
        while (departure + 1 < len(positions)
               and positions[departure + 1] == positions[0]):
            departure += 1
        return cls(positions[0], departure, positions[departure + 1:])

    @property
    def arrival(self) -> int:
        """The turn of the last position (when the drone is delivered)."""
        return self.departure + len(self.path)

    @property
    def last(self) -> Position:
        """The last position of the drone."""
        return self.path[-1] if self.path else self.origin

    def at(self, turn: int) -> Position:
        """Return the position at the end of a turn (0 to arrival)."""
        if turn <= self.departure:
            return self.origin
        return self.path[turn - self.departure - 1]

    def steps(self) -> Iterator[tuple[int, Position, Position]]:
        """Go through the turns after the departure.

        Yields:
            (turn, position before the turn, position after the turn) for
            every turn from departure + 1 to the arrival.
        """
        before = self.origin
        for turn, after in enumerate(self.path, start=self.departure + 1):
            yield turn, before, after
            before = after


class Schedule:
    """The timelines of all drones.

    Attributes:
        timelines: timelines[i] is the timeline of drone D<i+1>. It stops
            at the turn the drone reaches the end zone: delivered drones
            are no longer tracked.
    """

    def __init__(self, timelines: list[Timeline]) -> None:
        """Store the timelines and index the moves by turn.

        Args:
            timelines: One timeline per drone, in drone order.
        """
        self.timelines = timelines
        self._moves_by_turn: dict[int, list[tuple[int, Position]]] = {}
        for number, timeline in enumerate(timelines, start=1):
            for turn, before, after in timeline.steps():
                if after != before:
                    self._moves_by_turn.setdefault(turn, []).append(
                        (number, after)
                    )

    @property
    def total_turns(self) -> int:
        """Number of turns until the last drone is delivered."""
        if not self.timelines:
            return 0
        return max(timeline.arrival for timeline in self.timelines)

    @staticmethod
    def connection_used(
        network: Network, before: Position, after: Position,
    ) -> Connection | None:
        """Return the connection a drone uses during one turn.

        Args:
            network: The network.
            before: Position at the end of the previous turn.
            after: Position at the end of this turn.

        Returns:
            The connection crossed during the turn, or None if the drone
            stayed in its zone. A move into a restricted zone uses the
            connection during both of its turns.
        """
        if before.coming_from is not None:
            return network.find_connection(before.coming_from, before.zone)
        if after.coming_from is not None:
            return network.find_connection(after.coming_from, after.zone)
        if after.zone != before.zone:
            return network.find_connection(before.zone, after.zone)
        return None

    def changes(self, turn: int) -> list[tuple[int, Position]]:
        """List the drones that move during a turn.

        Args:
            turn: A turn number, from 1.

        Returns:
            (drone number, new position) for every drone whose position
            changed during the turn, ordered by drone number. Drones that
            wait or are already delivered are left out.
        """
        return self._moves_by_turn.get(turn, [])

    def lines(self, network: Network) -> list[str]:
        """Build the output, one line per turn.

        Args:
            network: The network, used to name connections.

        Returns:
            For each turn from 1, the moves of that turn separated by
            spaces, such as "D1-roof1 D2-hub-corridorA".
        """
        return [
            " ".join(f"D{number}-{self.label(network, position)}"
                     for number, position in self.changes(turn))
            for turn in range(1, self.total_turns + 1)
        ]

    @staticmethod
    def label(network: Network, position: Position) -> str:
        """Name a position as the output expects it.

        Args:
            network: The network, used to name connections.
            position: The position to name.

        Returns:
            The zone name, or the connection name while in transit.
        """
        if position.coming_from is None:
            return position.zone
        return network.find_connection(position.coming_from,
                                       position.zone).name
