#!/usr/bin/env python3

import sys

NO_SCORES = (
    "No scores provided. "
    "Usage: python3 ft_score_analytics.py <score1> <score2> ..."
)


def ft_score_analytics() -> None:
    print("=== Player Score Analytics ===")
    args = sys.argv[1:]
    if not args:
        print(NO_SCORES)
        return

    scores = []
    for arg in args:
        try:
            scores.append(int(arg))
        except ValueError:
            print(f"Invalid parameter: '{arg}'")

    if not scores:
        print(NO_SCORES)
        return

    total = sum(scores)
    print(f"Scores processed: {scores}")
    print(f"Total players: {len(scores)}")
    print(f"Total score: {total}")
    print(f"Average score: {total / len(scores)}")
    print(f"High score: {max(scores)}")
    print(f"Low score: {min(scores)}")
    print(f"Score range: {max(scores) - min(scores)}")


if __name__ == "__main__":
    ft_score_analytics()
