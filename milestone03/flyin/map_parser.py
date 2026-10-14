"""Read Fly-in map files and build the Network they describe."""
import re

from pydantic import ValidationError

from models import Connection, Network, Zone, ZoneType

INT_PATTERN = re.compile(r"[+-]?[0-9]+")
MAX_DIGITS = 18
MAX_DRONES = 10000
ZONE_KEYS = frozenset({"zone", "color", "max_drones"})
CONNECTION_KEYS = frozenset({"max_link_capacity"})
ZONE_TYPE_NAMES = "normal, blocked, restricted or priority"


class ParseError(Exception):
    """Error in a map file, with the line number when there is one."""

    def __init__(self, line_nbr: int | None, message: str) -> None:
        """Build the message, adding "line N: " in front when known.

        Args:
            line_nbr: Line number in the file, or None when the error is
                not about one line (for example a missing start_hub).
            message: What is wrong.
        """
        if line_nbr is not None:
            message = f"line {line_nbr}: {message}"
        super().__init__(message)


class MapParser:
    """Turn the text of a map file into a Network."""

    def parse_file(self, path: str) -> Network:
        """Read a map file and parse it.

        Args:
            path: Path of the map file.

        Returns:
            The network described by the file.

        Raises:
            ParseError: If the file cannot be read or is not a valid map.
        """
        try:
            with open(path, encoding="utf-8") as file:
                lines = file.read().splitlines()
        except UnicodeDecodeError:
            raise ParseError(
                None, f"cannot read '{path}': not a UTF-8 text file"
            ) from None
        except OSError as error:
            raise ParseError(
                None, f"cannot read '{path}': {error.strerror or error}"
            ) from None
        return self.parse_lines(lines)

    def parse_lines(self, lines: list[str]) -> Network:
        """Parse the lines of a map file.

        Everything after a '#' is a comment and is ignored, whether the
        '#' starts the line or not. Lines left empty are skipped. The line
        numbers in error messages count every line, including those.

        Args:
            lines: The lines of the file, without newline characters.

        Returns:
            The network described by the lines.

        Raises:
            ParseError: If a line is invalid, or if nb_drones, start_hub or
                end_hub is missing.
        """
        network: Network | None = None
        for line_nbr, raw_line in enumerate(lines, start=1):
            line = raw_line.partition("#")[0].strip()
            if line == "":
                continue
            try:
                network = self._parse_line(network, line)
            except ValidationError as error:
                first = error.errors()[0]
                field = ".".join(str(part) for part in first["loc"])
                raise ParseError(
                    line_nbr, f"{field}: {first['msg']}"
                ) from None
            except ValueError as error:
                raise ParseError(line_nbr, str(error)) from None
        if network is None:
            raise ParseError(None, "the map file is empty")
        if network.start is None:
            raise ParseError(None, "missing start_hub")
        if network.end is None:
            raise ParseError(None, "missing end_hub")
        return network

    def _parse_line(self, network: Network | None, line: str) -> Network:
        """Apply one line to the network.

        Args:
            network: The network built so far, or None before the
                nb_drones line.
            line: One line, already stripped, that is not a comment.

        Returns:
            The network after this line (a new one for nb_drones).

        Raises:
            ValueError: If the line is invalid.
        """
        kind, colon, rest = line.partition(":")
        kind = kind.strip()
        rest = rest.strip()
        if network is None:
            if kind != "nb_drones" or colon == "":
                raise ValueError(
                    "first line must be 'nb_drones: <positive_integer>'"
                )
            return Network(self._parse_nb_drones(rest))
        if colon == "":
            raise ValueError("missing ':' after the line type")
        if kind == "nb_drones":
            raise ValueError("nb_drones is defined more than once")
        if kind == "hub":
            network.add_zone(self._parse_zone(rest, is_hub_end=False))
        elif kind == "start_hub" or kind == "end_hub":
            zone = self._parse_zone(rest, is_hub_end=True)
            if zone.zone_type == ZoneType.BLOCKED:
                raise ValueError(f"{kind} '{zone.name}' cannot be blocked")
            network.add_zone(zone)
            if kind == "start_hub":
                network.set_start(zone.name)
            else:
                network.set_end(zone.name)
        elif kind == "connection":
            network.add_connection(self._parse_connection(rest))
        else:
            raise ValueError(f"unknown line type '{kind}'")
        return network

    def _parse_nb_drones(self, text: str) -> int:
        """Read the value of the nb_drones line.

        Args:
            text: The text after "nb_drones:".

        Returns:
            The number. Network checks that it is positive.

        Raises:
            ValueError: If the text is not an integer, or if it is larger
                than MAX_DRONES.
        """
        if not INT_PATTERN.fullmatch(text):
            raise ValueError(f"invalid number of drones '{self._short(text)}'")
        if text.startswith("-"):
            raise ValueError("number of drones must be a positive integer, "
                             f"got {self._short(text)}")
        digits = text.lstrip("+")
        if len(digits) > len(str(MAX_DRONES)) or int(digits) > MAX_DRONES:
            raise ValueError(f"number of drones must be at most {MAX_DRONES}, "
                             f"got {self._short(text)}")
        return int(digits)

    @staticmethod
    def _to_int(text: str) -> int | None:
        """Return the integer written in text, or None if it is not one.

        Numbers longer than MAX_DIGITS digits are refused: no map needs
        them, and Python refuses to convert very long strings anyway.
        """
        if (not INT_PATTERN.fullmatch(text)
                or len(text.lstrip("+-")) > MAX_DIGITS):
            return None
        return int(text)

    @staticmethod
    def _short(text: str) -> str:
        """Cut a long text for an error message."""
        return text if len(text) <= 20 else text[:20] + "..."

    def _split_metadata(
        self, text: str, allowed_keys: frozenset[str],
    ) -> tuple[str, dict[str, str]]:
        """Separate the "[key=value ...]" part from the rest of a line.

        Args:
            text: For example "roof1 3 4 [zone=restricted color=red]".
            allowed_keys: The keys that may appear in the brackets.

        Returns:
            The text before the brackets, and the metadata as a dict. For
            the example: ("roof1 3 4", {"zone": "restricted",
            "color": "red"}).

        Raises:
            ValueError: If the brackets or a key=value pair are invalid.
        """
        body, bracket, inside = text.partition("[")
        metadata: dict[str, str] = {}
        if bracket == "":
            if "]" in body:
                raise ValueError(
                    "metadata must be enclosed in one pair of '[' and ']'"
                )
            return body.strip(), metadata
        if (not inside.endswith("]") or "[" in inside
                or "]" in inside[:-1]):
            raise ValueError(
                "metadata must be enclosed in one pair of '[' and ']'"
            )
        for token in inside[:-1].split():
            key, equal, value = token.partition("=")
            if equal == "" or key == "" or value == "":
                raise ValueError(
                    f"invalid metadata '{token}' (expected key=value)"
                )
            if key not in allowed_keys:
                raise ValueError(f"unknown metadata key '{key}'")
            if key in metadata:
                raise ValueError(
                    f"metadata key '{key}' is given more than once"
                )
            metadata[key] = value
        return body.strip(), metadata

    def _parse_zone(self, text: str, is_hub_end: bool) -> Zone:
        """Build a Zone from the text after "hub:", "start_hub:" or
        "end_hub:".

        Args:
            text: For example "roof1 3 4 [zone=restricted color=red]".
            is_hub_end: True for start_hub and end_hub. Their max_drones
                is ignored, because they have no capacity limit.

        Returns:
            The zone.

        Raises:
            ValueError: If the text is not a valid zone definition.
        """
        body, metadata = self._split_metadata(text, ZONE_KEYS)
        parts = body.split()
        if len(parts) != 3:
            raise ValueError(
                f"expected '<name> <x> <y> [metadata]', got '{text}'"
            )
        name, x_text, y_text = parts
        if "-" in name:
            raise ValueError(f"zone name '{name}' must not contain '-'")
        max_drones = 1
        if "max_drones" in metadata and not is_hub_end:
            max_drones = self._parse_positive_int(
                "max_drones", metadata["max_drones"]
            )
        return Zone(
            name=name,
            x=self._parse_coordinate(x_text),
            y=self._parse_coordinate(y_text),
            zone_type=self._parse_zone_type(metadata.get("zone", "normal")),
            color=metadata.get("color"),
            max_drones=max_drones,
        )

    def _parse_connection(self, text: str) -> Connection:
        """Build a Connection from the text after "connection:".

        Args:
            text: For example "hub-roof1 [max_link_capacity=2]".

        Returns:
            The connection.

        Raises:
            ValueError: If the text is not a valid connection definition.
        """
        body, metadata = self._split_metadata(text, CONNECTION_KEYS)
        zone1, dash, zone2 = body.partition("-")
        if (
            len(body.split()) != 1 or dash == "" or zone1 == ""
            or zone2 == "" or "-" in zone2
        ):
            raise ValueError(
                f"expected '<zone1>-<zone2> [metadata]', got '{text}'"
            )
        if zone1 == zone2:
            raise ValueError(
                f"connection {zone1}-{zone2} must link two different zones"
            )
        capacity = 1
        if "max_link_capacity" in metadata:
            capacity = self._parse_positive_int(
                "max_link_capacity", metadata["max_link_capacity"]
            )
        return Connection(
            zone1=zone1, zone2=zone2, max_link_capacity=capacity
        )

    def _parse_coordinate(self, text: str) -> int:
        """Read one coordinate. Negative numbers are allowed.

        Raises:
            ValueError: If the text is not an integer.
        """
        value = self._to_int(text)
        if value is None:
            raise ValueError(
                f"invalid coordinate '{self._short(text)}' "
                f"(must be an integer of at most {MAX_DIGITS} digits)"
            )
        return value

    def _parse_positive_int(self, key: str, text: str) -> int:
        """Read a capacity value such as max_drones.

        Raises:
            ValueError: If the text is not an integer greater than 0.
        """
        value = self._to_int(text)
        if value is None or value < 1:
            raise ValueError(
                f"invalid {key} '{self._short(text)}' (must be a positive "
                f"integer of at most {MAX_DIGITS} digits)"
            )
        return value

    def _parse_zone_type(self, text: str) -> ZoneType:
        """Turn the value of "zone=" into a ZoneType.

        Raises:
            ValueError: If the value is not one of the four zone types.
        """
        try:
            return ZoneType(text)
        except ValueError:
            raise ValueError(
                f"invalid zone type '{text}' (expected {ZONE_TYPE_NAMES})"
            ) from None
