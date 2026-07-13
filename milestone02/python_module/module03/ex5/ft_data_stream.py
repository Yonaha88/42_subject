#!/usr/bin/env python3

import random
from typing import Generator

PLAYERS = ["alice", "bob", "charlie", "dylan"]
ACTIONS = ["run", "jump", "move", "grab", "use", "swim", "eat", "fight"]


def gen_event() -> Generator[tuple[str, str], None, None]:
    while True:
        yield (random.choice(PLAYERS), random.choice(ACTIONS))


def consume_event(
    events: list[tuple[str, str]],
) -> Generator[tuple[str, str], None, None]:
    while len(events) > 0:
        idx = random.randint(0, len(events) - 1)
        event = events[idx]
        del events[idx]
        yield event


if __name__ == "__main__":
    print("=== Game Data Stream Processor ===")
    gen = gen_event()
    for i in range(1000):
        name, action = next(gen)
        print(f"Event {i}: Player {name} did action {action}")
    event_list: list[tuple[str, str]] = [next(gen) for _ in range(10)]
    print(f"Built list of 10 events: {event_list}")
    print()
    for event in consume_event(event_list):
        print(f"Got event from list: {event}")
        print(f"Remains in list: {event_list}")
