"""Distances on the map with Dijkstra's algorithm.

This search looks at the map only. It does not know about the other
drones, so it ignores zone and connection capacities. The planner uses
its result as a lower bound: a drone in zone Z can never reach the end
zone in fewer turns than turns_to_end()[Z].
"""
import heapq

from models import Network


class NoPathError(Exception):
    """There is no route from the start zone to the end zone."""


class PathFinder:
    """Dijkstra's algorithm on the zones of a network."""

    def turns_to_end(self, network: Network) -> dict[str, int]:
        """Compute, for every zone, the fewest turns needed to reach the end.

        Entering a zone costs its zone type cost (1 for normal and
        priority, 2 for restricted). Blocked zones are never entered. The
        search starts from the end zone and walks the connections
        backwards.

        Args:
            network: A parsed network, with its start and end zones set.

        Returns:
            The number of turns for every zone that can reach the end zone.
            Zones that cannot reach it are missing from the dict.

        Raises:
            NoPathError: If the start zone cannot reach the end zone.
            ValueError: If the start or end zone is not set.
        """
        start, end = network.start, network.end
        if start is None or end is None:
            raise ValueError("the start and end zones must be set")
        turns: dict[str, int] = {}
        queue: list[tuple[int, str]] = [(0, end)]
        while queue:
            cost, zone_name = heapq.heappop(queue)
            if zone_name in turns:
                continue
            turns[zone_name] = cost
            step = network.zones[zone_name].zone_type.cost
            if step is None:
                continue
            for connection in network.neighbors(zone_name):
                previous = connection.other(zone_name)
                if network.zones[previous].zone_type.cost is None:
                    continue
                if previous not in turns:
                    heapq.heappush(queue, (cost + step, previous))
        if start not in turns:
            raise NoPathError(f"no path from '{start}' to '{end}'")
        return turns
