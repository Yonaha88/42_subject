#!/usr/bin/env python3

import sys


def ft_command_quest() -> None:
    print("=== Command Quest ===")
    print(f"Program name: {sys.argv[0]}")
    arg = sys.argv[1:]
    index = 0
    if arg:
        print(f"Arguments received: {len(arg)}")
        for arg_str in arg:
            index += 1
            print(f"Argument {index}: {arg_str}")
    else:
        print("No arguments provided!")
    print(f"Total arguments: {index + 1}")


if __name__ == "__main__":
    ft_command_quest()
