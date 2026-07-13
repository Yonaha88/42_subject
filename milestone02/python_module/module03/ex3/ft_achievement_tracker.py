#!/usr/bin/env python3

import random

ALL_ACHIEVEMENTS = [
    "First Steps", "Boss Slayer", "Speed Runner", "Collector Supreme",
    "Master Explorer", "World Savior", "Crafting Genius", "Strategist",
    "Unstoppable", "Untouchable", "Survivor", "Sharp Mind",
    "Treasure Hunter", "Hidden Path Finder",
]

PLAYERS = ["Alice", "Bob", "Charlie", "Dylan"]


def gen_player_achievements() -> set[str]:
    count = random.randint(4, 10)
    return set(random.sample(ALL_ACHIEVEMENTS, count))


def main() -> None:
    print("=== Achievement Tracker System ===")
    print()

    player_achievements: dict[str, set[str]] = {}
    for player in PLAYERS:
        player_achievements[player] = gen_player_achievements()
        print(f"Player {player}: {player_achievements[player]}")

    print()
    all_achievements: set[str] = set()
    for player in PLAYERS:
        all_achievements = all_achievements.union(
            player_achievements[player]
        )
    print(f"All distinct achievements: {all_achievements}")

    print()
    common = player_achievements[PLAYERS[0]]
    for player in PLAYERS[1:]:
        common = common.intersection(player_achievements[player])
    print(f"Common achievements: {common}")

    print()
    for player in PLAYERS:
        others: set[str] = set()
        for other in PLAYERS:
            if other != player:
                others = others.union(player_achievements[other])
        exclusive = player_achievements[player].difference(others)
        print(f"Only {player} has: {exclusive}")

    print()
    all_set = set(ALL_ACHIEVEMENTS)
    for player in PLAYERS:
        missing = all_set.difference(player_achievements[player])
        print(f"{player} is missing: {missing}")


if __name__ == "__main__":
    main()
