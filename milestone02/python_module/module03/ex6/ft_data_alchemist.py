#!/usr/bin/env python3

import random

PLAYERS = [
    "Alice", "bob", "Charlie", "dylan", "Emma",
    "Gregory", "john", "kevin", "Liam",
]


def main() -> None:
    print("=== Game Data Alchemist ===")
    print()

    print(f"Initial list of players: {PLAYERS}")
    print()

    capitalized = [name.capitalize() for name in PLAYERS]
    print(f"New list with all names capitalized: {capitalized}")
    print()

    already_cap = [name for name in PLAYERS if name[0].isupper()]
    print(f"New list of capitalized names only: {already_cap}")
    print()

    score_dict = {
        name: random.randint(0, 1000) for name in capitalized
    }
    print(f"Score dict: {score_dict}")
    print()

    total = sum(score_dict[k] for k in score_dict)
    avg = round(total / len(score_dict), 2)
    print(f"Score average is {avg}")
    high_scores = {
        name: score_dict[name]
        for name in score_dict
        if score_dict[name] > avg
    }
    print(f"High scores: {high_scores}")


if __name__ == "__main__":
    main()
