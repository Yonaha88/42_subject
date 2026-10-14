"""Plan every drone with a reservation table (prioritized planning).

The drones are planned one after another. Each drone searches for its
earliest arrival with Dijkstra's algorithm over (zone, turn) states,
while respecting what the drones planned before it have reserved. Its
own route is then reserved in turn, so the next drones go around it.
"""
import heapq
from dataclasses import dataclass

from models import Connection, Network, ZoneType
from pathfinder import NoPathError, PathFinder
from schedule import Position, Schedule, Timeline


class ReservationTable:
    """How many drones use each zone and connection at each turn."""

    def __init__(self, network: Network) -> None:
        """Create an empty table.

        Args:
            network: The network the reservations are made on.
        """
        self._network = network
        self._zone_use: dict[tuple[str, int], int] = {}
        self._link_use: dict[tuple[str, int], int] = {}
        self.last_turn = 0

    def zone_has_room(self, zone_name: str, turn: int) -> bool:
        """Tell if one more drone can be in a zone at the end of a turn.

        The start and end zones have no limit.
        """
        if zone_name in (self._network.start, self._network.end):
            return True
        used = self._zone_use.get((zone_name, turn), 0)
        return used < self._network.zones[zone_name].max_drones

    def link_has_room(self, connection: Connection, turn: int) -> bool:
        """Tell if one more drone can use a connection during a turn."""
        used = self._link_use.get((connection.name, turn), 0)
        return used < connection.max_link_capacity

    def reserve(self, timeline: Timeline) -> None:
        """Book every zone and connection a drone uses.

        The turns spent waiting in the start zone are skipped: the start
        zone has no limit and no connection is used.

        Args:
            timeline: The timeline of the drone.
        """
        unlimited = (self._network.start, self._network.end)
        for turn, before, after in timeline.steps():
            if not after.in_transit and after.zone not in unlimited:
                key = (after.zone, turn)
                self._zone_use[key] = self._zone_use.get(key, 0) + 1
            link = Schedule.connection_used(self._network, before, after)
            if link is not None:
                key = (link.name, turn)
                self._link_use[key] = self._link_use.get(key, 0) + 1
        self.last_turn = max(self.last_turn, timeline.arrival)


@dataclass(frozen=True)
class _Move:
    """One possible move from a (zone, turn) state.

    Attributes:
        zone: The zone the drone is in after the move.
        turn: The turn at which it is there.
        transit: True if the move flies into a restricted zone (the turn
            before `turn` is spent on the connection).
    """

    zone: str
    turn: int
    transit: bool


class Planner:
    """Plan all drones so that they are delivered as early as possible."""

    def plan(self, network: Network) -> Schedule:
        """Plan every drone, one after another.

        Args:
            network: A parsed network.

        Returns:
            The schedule of all drones.

        Raises:
            NoPathError: If the end zone cannot be reached.
        """
        turns_to_end = PathFinder().turns_to_end(network)
        overtake = turns_to_end[str(network.start)]
        table = ReservationTable(network)
        timelines: list[Timeline] = []
        first_turn = 0
        for _ in range(network.nb_drones):
            timeline = self._plan_drone(network, table, turns_to_end,
                                        first_turn)
            table.reserve(timeline)
            timelines.append(timeline)
            first_turn = max(0, timeline.departure - overtake)
        return Schedule(timelines)

    def _plan_drone(
        self, network: Network, table: ReservationTable,
        turns_to_end: dict[str, int], first_turn: int,
    ) -> Timeline:
        """Find the earliest arrival of one drone.

        This is Dijkstra's algorithm on (zone, turn) states, guided by
        turns_to_end (an A* search). From a state the drone can wait, move
        to a normal or priority zone (1 turn) or fly to a restricted zone
        (2 turns, landing is forced). A move is only allowed if the
        reservation table still has room.

        When two routes arrive at the same turn, the one that goes through
        more priority zones wins, then the one that spends fewer turns in
        zones with a capacity limit (so that it leaves room for others).

        The drones leave the start zone roughly in order, so the search
        begins at first_turn: a few turns before the previous drone left,
        not at turn 0. A drone may still overtake the previous one by a
        short route, but the search no longer walks through all the early
        turns, which keeps it fast when there are thousands of drones.

        Args:
            network: The network.
            table: What the previous drones have reserved.
            turns_to_end: Lower bound of the remaining turns, per zone.
            first_turn: The drone waits in the start zone until this turn.

        Returns:
            The timeline of the drone, from turn 0 to its arrival.

        Raises:
            NoPathError: If no arrival is found. This does not happen when
                the end zone is reachable, because waiting in the start
                zone is always allowed and the reservations end.
        """
        start, end = str(network.start), str(network.end)
        origin = (start, first_turn)
        limit = max(table.last_turn, first_turn) + turns_to_end[start]
        best: dict[tuple[str, int], tuple[int, int]] = {origin: (0, 0)}
        came_from: dict[tuple[str, int], tuple[str, int]] = {}
        through_transit: set[tuple[str, int]] = set()
        done: set[tuple[str, int]] = set()
        queue = [(first_turn + turns_to_end[start], first_turn, 0, 0, start)]
        while queue:
            _, turn, priority_score, busy, zone_name = heapq.heappop(queue)
            if (zone_name, turn) in done:
                continue
            done.add((zone_name, turn))
            if zone_name == end:
                return self._timeline(origin, (end, turn), came_from,
                                      through_transit)
            if turn >= limit:
                continue
            for move in self._moves(network, table, zone_name, turn):
                key = (move.zone, move.turn)
                if key in done or move.zone not in turns_to_end:
                    continue
                zone_type = network.zones[move.zone].zone_type
                entered_priority = (move.zone != zone_name
                                    and zone_type == ZoneType.PRIORITY)
                score = (
                    priority_score - int(entered_priority),
                    busy + int(move.zone not in (start, end)),
                )
                if key in best and best[key] <= score:
                    continue
                best[key] = score
                came_from[key] = (zone_name, turn)
                if move.transit:
                    through_transit.add(key)
                else:
                    through_transit.discard(key)
                estimate = move.turn + turns_to_end[move.zone]
                heapq.heappush(
                    queue, (estimate, move.turn, *score, move.zone)
                )
        raise NoPathError(f"no path from '{start}' to '{end}'")

    def _moves(
        self, network: Network, table: ReservationTable, zone_name: str,
        turn: int,
    ) -> list[_Move]:
        """List the moves allowed from a zone at a turn.

        Args:
            network: The network.
            table: What the previous drones have reserved.
            zone_name: Where the drone is at the end of `turn`.
            turn: The current turn.

        Returns:
            Waiting (if the zone keeps room), then every move to a
            neighbour that the capacities allow.
        """
        moves: list[_Move] = []
        if table.zone_has_room(zone_name, turn + 1):
            moves.append(_Move(zone_name, turn + 1, False))
        for connection in network.neighbors(zone_name):
            target = connection.other(zone_name)
            zone_type = network.zones[target].zone_type
            if zone_type == ZoneType.BLOCKED:
                continue
            if not table.link_has_room(connection, turn + 1):
                continue
            if zone_type == ZoneType.RESTRICTED:
                if (table.link_has_room(connection, turn + 2)
                        and table.zone_has_room(target, turn + 2)):
                    moves.append(_Move(target, turn + 2, True))
            elif table.zone_has_room(target, turn + 1):
                moves.append(_Move(target, turn + 1, False))
        return moves

    def _timeline(
        self, origin: tuple[str, int], arrival: tuple[str, int],
        came_from: dict[tuple[str, int], tuple[str, int]],
        through_transit: set[tuple[str, int]],
    ) -> Timeline:
        """Rebuild the timeline of a drone from the search result.

        Args:
            origin: The (start zone, first turn) state the search began at.
            arrival: The (end zone, turn) state that was reached.
            came_from: For each state, the state it was reached from.
            through_transit: The states reached by flying into a
                restricted zone.

        Returns:
            The timeline, whose departure is the last turn spent in the
            start zone before the first move.
        """
        states = [arrival]
        while states[-1] != origin:
            states.append(came_from[states[-1]])
        states.reverse()
        start, first_turn = origin
        path: list[Position] = []
        for (previous, _), state in zip(states, states[1:]):
            zone_name = state[0]
            if state in through_transit:
                path.append(Position(zone_name, coming_from=previous))
            path.append(Position(zone_name))
        waiting = 0
        while waiting < len(path) and path[waiting] == Position(start):
            waiting += 1
        return Timeline(Position(start), first_turn + waiting,
                        path[waiting:])
