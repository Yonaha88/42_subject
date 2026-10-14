"""Check that a schedule follows every rule of the simulation.

The validator does not trust the planner: it replays every drone turn by
turn and reports every broken rule. It is used by main.py before printing
anything, and by the tests.
"""
from models import Network, ZoneType
from schedule import Position, Schedule, Timeline


class ScheduleValidator:
    """Replay a schedule and collect the rules it breaks."""

    def validate(self, network: Network, schedule: Schedule) -> list[str]:
        """Check a schedule.

        Args:
            network: The network the schedule was made for.
            schedule: The schedule to check.

        Returns:
            One message per broken rule. An empty list means the schedule
            is valid.
        """
        if network.start is None or network.end is None:
            return ["the start and end zones must be set"]
        start, end = Position(network.start), Position(network.end)
        errors: list[str] = []
        if len(schedule.timelines) != network.nb_drones:
            errors.append(
                f"expected {network.nb_drones} drones, "
                f"got {len(schedule.timelines)}"
            )
        for number, timeline in enumerate(schedule.timelines, start=1):
            errors.extend(
                self._check_drone(network, f"D{number}", timeline, start, end)
            )
        if not errors:
            errors.extend(self._check_capacities(network, schedule))
        return errors

    def _check_drone(
        self, network: Network, drone: str, timeline: Timeline,
        start: Position, end: Position,
    ) -> list[str]:
        """Check the moves of one drone on its own.

        Args:
            network: The network.
            drone: The drone name, such as "D1", for the messages.
            timeline: The timeline of the drone.
            start: The position in the start zone.
            end: The position in the end zone.

        Returns:
            The broken rules found for this drone.
        """
        if timeline.origin != start:
            return [f"{drone} does not start in the start zone"]
        if timeline.last != end:
            return [f"{drone} does not end in the end zone"]
        errors: list[str] = []
        for turn, before, after in timeline.steps():
            problem = self._check_move(network, before, after)
            if problem is not None:
                errors.append(f"{drone} turn {turn}: {problem}")
            if after == end and turn != timeline.arrival:
                errors.append(
                    f"{drone} turn {turn}: still tracked after delivery"
                )
        return errors

    def _check_move(
        self, network: Network, before: Position, after: Position,
    ) -> str | None:
        """Check one turn of one drone.

        Args:
            network: The network.
            before: Position at the end of the previous turn.
            after: Position at the end of this turn.

        Returns:
            What is wrong with the move, or None if it is allowed.
        """
        if after.zone not in network.zones:
            return f"unknown zone '{after.zone}'"
        target_type = network.zones[after.zone].zone_type
        if before.in_transit:
            if after != Position(before.zone):
                return (f"must land in '{before.zone}' right after "
                        "flying on the connection")
            return None
        if after == before:
            return None
        origin = after.coming_from if after.in_transit else before.zone
        if origin != before.zone:
            return f"cannot fly from '{origin}' while in '{before.zone}'"
        try:
            network.find_connection(before.zone, after.zone)
        except ValueError:
            return f"'{before.zone}' and '{after.zone}' are not connected"
        if target_type == ZoneType.BLOCKED:
            return f"cannot enter blocked zone '{after.zone}'"
        if target_type == ZoneType.RESTRICTED and not after.in_transit:
            return (f"moving into restricted zone '{after.zone}' "
                    "must take two turns")
        if target_type != ZoneType.RESTRICTED and after.in_transit:
            return f"'{after.zone}' is not restricted: no transit turn"
        return None

    def _check_capacities(
        self, network: Network, schedule: Schedule,
    ) -> list[str]:
        """Check zone and connection capacities at every turn.

        Zones are counted at the end of each turn, so a drone leaving a
        zone frees its place for a drone arriving in the same turn. The
        start and end zones have no limit, so the turns a drone waits in
        the start zone are not counted.

        Args:
            network: The network.
            schedule: The schedule, already checked drone by drone.

        Returns:
            One message per exceeded capacity, in turn order.
        """
        unlimited = {network.start, network.end}
        in_zone: dict[tuple[int, str], int] = {}
        on_link: dict[tuple[int, str], int] = {}
        for timeline in schedule.timelines:
            for turn, before, after in timeline.steps():
                if not after.in_transit and after.zone not in unlimited:
                    key = (turn, after.zone)
                    in_zone[key] = in_zone.get(key, 0) + 1
                link = Schedule.connection_used(network, before, after)
                if link is not None:
                    key = (turn, link.name)
                    on_link[key] = on_link.get(key, 0) + 1
        errors: list[tuple[int, str]] = []
        for (turn, name), count in in_zone.items():
            limit = network.zones[name].max_drones
            if count > limit:
                errors.append((turn, f"turn {turn}: zone '{name}' holds "
                                     f"{count} drones (max {limit})"))
        capacity = {c.name: c.max_link_capacity for c in network.connections}
        for (turn, name), count in on_link.items():
            if count > capacity[name]:
                errors.append((turn, f"turn {turn}: connection '{name}' is "
                                     f"used by {count} drones "
                                     f"(max {capacity[name]})"))
        return [message for _, message in sorted(errors)]
