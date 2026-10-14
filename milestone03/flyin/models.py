"""Data models for the Fly-in drone network.

A map file is turned into one Network, which holds Zones (the nodes)
and Connections (the two-way edges between them).
"""
from enum import Enum
from pydantic import BaseModel, Field


class ZoneType(Enum):
    """Kind of a zone, as written in ``zone=<type>`` in a map file."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int | None:
        """Number of turns needed to move into a zone of this type.

        Returns:
            1 for normal and priority zones, 2 for restricted zones,
            and None for blocked zones, which can never be entered.
        """
        if self == ZoneType.NORMAL or self == ZoneType.PRIORITY:
            return 1
        elif self == ZoneType.BLOCKED:
            return None
        elif self == ZoneType.RESTRICTED:
            return 2


class Zone(BaseModel):
    """A zone (node) of the network.

    Attributes:
        name: Unique name of the zone.
        x: X coordinate.
        y: Y coordinate.
        zone_type: Kind of the zone. Defaults to normal.
        color: Color used for display, or None if not given.
        max_drones: How many drones can be in the zone at the same time.
            Must be positive. Defaults to 1.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = Field(default=ZoneType.NORMAL)
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1, gt=0)


class Connection(BaseModel):
    """A two-way connection (edge) between two zones.

    Attributes:
        zone1: Name of the zone at one end.
        zone2: Name of the zone at the other end.
        max_link_capacity: How many drones can use the connection at the
            same time. Must be positive. Defaults to 1.
    """

    zone1: str
    zone2: str
    max_link_capacity: int = Field(default=1, gt=0)

    @property
    def name(self) -> str:
        """Name used in the output, such as "hub-roof1".

        The two zones are written in the same order as in the map file.
        """
        return f"{self.zone1}-{self.zone2}"

    def other(self, zone_name: str) -> str:
        """Return the zone at the other end of this connection.

        Args:
            zone_name: Name of the zone at one end.

        Returns:
            Name of the zone at the opposite end.

        Raises:
            ValueError: If zone_name is not an end of this connection.
        """
        if self.zone1 == zone_name:
            return self.zone2
        elif self.zone2 == zone_name:
            return self.zone1
        else:
            raise ValueError(
                f"'{zone_name}' is not an end of connection "
                f"{self.zone1}-{self.zone2}"
            )


class Network:
    """The whole drone network: zones, connections and the two hubs.

    Attributes:
        nb_drones: Number of drones that start at the start zone.
        zones: Zones by name.
        connections: All connections, in the order they were added.
        adjacency: For each zone name, the connections that touch it.
        start: Name of the start zone, or None until it is set.
        end: Name of the end zone, or None until it is set.
        connection_keys: Both zone names of every connection, stored
            without order so that a-b and b-a are seen as the same.
        coordinates: The zone name at each (x, y), to refuse two zones
            at the same place.
    """

    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    adjacency: dict[str, list[Connection]]
    start: str | None
    end: str | None
    connection_keys: set[frozenset[str]]
    coordinates: dict[tuple[int, int], str]

    def __init__(self, nb_drones: int) -> None:
        """Create an empty network.

        Args:
            nb_drones: Number of drones. Must be positive.

        Raises:
            ValueError: If nb_drones is not positive.
        """
        if nb_drones < 1:
            raise ValueError(
                "number of drones must be a positive integer, "
                f"got {nb_drones}"
            )
        self.nb_drones = nb_drones
        self.zones = {}
        self.connections = []
        self.adjacency = {}
        self.start = None
        self.end = None
        self.connection_keys = set()
        self.coordinates = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the network.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with the same name, or at the same
                coordinates, already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"duplicate zone name '{zone.name}'")
        place = (zone.x, zone.y)
        if place in self.coordinates:
            raise ValueError(
                f"zones '{self.coordinates[place]}' and '{zone.name}' "
                f"have the same coordinates ({zone.x}, {zone.y})"
            )
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []
        self.coordinates[place] = zone.name

    def set_start(self, zone_name: str) -> None:
        """Mark an existing zone as the start zone.

        Args:
            zone_name: Name of the zone where all drones start.

        Raises:
            ValueError: If the start zone is already set, or if the zone
                does not exist.
        """
        if self.start is not None:
            raise ValueError(
                f"start zone is already defined as '{self.start}'"
            )
        if zone_name not in self.zones:
            raise ValueError(
                f"start zone '{zone_name}' is not defined"
            )
        self.start = zone_name

    def set_end(self, zone_name: str) -> None:
        """Mark an existing zone as the end zone.

        Args:
            zone_name: Name of the zone where all drones must arrive.

        Raises:
            ValueError: If the end zone is already set, or if the zone
                does not exist.
        """
        if self.end is not None:
            raise ValueError(
                f"end zone is already defined as '{self.end}'"
            )
        if zone_name not in self.zones:
            raise ValueError(
                f"end zone '{zone_name}' is not defined"
            )
        self.end = zone_name

    def add_connection(self, connection: Connection) -> None:
        """Add a two-way connection between two existing zones.

        Args:
            connection: The connection to add.

        Raises:
            ValueError: If one of its zones does not exist, or if the same
                connection was already added (a-b and b-a are the same).
        """
        if connection.zone1 not in self.zones:
            raise ValueError(
                f"connection {connection.zone1}-{connection.zone2} "
                f"refers to undefined zone '{connection.zone1}'"
            )
        if connection.zone2 not in self.zones:
            raise ValueError(
                f"connection {connection.zone1}-{connection.zone2} "
                f"refers to undefined zone '{connection.zone2}'"
            )
        key = frozenset((connection.zone1, connection.zone2))
        if key in self.connection_keys:
            raise ValueError(
                f"duplicate connection {connection.zone1}-{connection.zone2}"
            )
        self.connection_keys.add(key)
        self.connections.append(connection)
        self.adjacency[connection.zone1].append(connection)
        self.adjacency[connection.zone2].append(connection)

    def neighbors(self, zone_name: str) -> list[Connection]:
        """Return the connections that touch a zone.

        Args:
            zone_name: Name of the zone.

        Returns:
            The connections that have this zone at one of their ends.

        Raises:
            ValueError: If the zone does not exist.
        """
        if zone_name not in self.adjacency:
            raise ValueError(f"zone '{zone_name}' is not defined")
        return self.adjacency[zone_name]

    def find_connection(self, zone_a: str, zone_b: str) -> Connection:
        """Return the connection between two zones.

        Args:
            zone_a: Name of one zone.
            zone_b: Name of the other zone.

        Returns:
            The connection that links the two zones, in either direction.

        Raises:
            ValueError: If the two zones are not connected.
        """
        for connection in self.neighbors(zone_a):
            if connection.other(zone_a) == zone_b:
                return connection
        raise ValueError(f"zones '{zone_a}' and '{zone_b}' are not connected")
