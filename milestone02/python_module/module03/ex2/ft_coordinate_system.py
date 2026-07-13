#!/usr/bin/env python3

import math


def get_player_pos() -> tuple[float, float, float]:
    while True:
        line = input(
            "Enter new coordinates as floats in format 'x,y,z': "
        )
        try:
            x_str, y_str, z_str = line.split(",")
        except ValueError:
            print("Invalid syntax")
            continue
        try:
            x = float(x_str.strip())
        except ValueError as e:
            print(f"Error on parameter '{x_str.strip()}': {e}")
            continue
        try:
            y = float(y_str.strip())
        except ValueError as e:
            print(f"Error on parameter '{y_str.strip()}': {e}")
            continue
        try:
            z = float(z_str.strip())
        except ValueError as e:
            print(f"Error on parameter '{z_str.strip()}': {e}")
            continue
        return (x, y, z)


def dist(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
) -> float:
    return math.sqrt(
        (p2[0] - p1[0]) ** 2
        + (p2[1] - p1[1]) ** 2
        + (p2[2] - p1[2]) ** 2
    )


if __name__ == "__main__":
    print("=== Game Coordinate System ===")
    print()
    print("Get a first set of coordinates")
    pos1 = get_player_pos()
    print(f"Got a first tuple: {pos1}")
    print(f"It includes: X={pos1[0]}, Y={pos1[1]}, Z={pos1[2]}")
    center: tuple[float, float, float] = (0.0, 0.0, 0.0)
    print(f"Distance to center: {round(dist(pos1, center), 4)}")
    print()
    print("Get a second set of coordinates")
    pos2 = get_player_pos()
    d = round(dist(pos1, pos2), 4)
    print(f"Distance between the 2 sets of coordinates: {d}")
