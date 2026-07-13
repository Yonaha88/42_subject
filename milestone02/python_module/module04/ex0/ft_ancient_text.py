#!/usr/bin/env python3

import sys


def display_file(filename: str) -> None:
    print("=== Cyber Archives Recovery ===")
    print(f"Accessing file '{filename}'")
    try:
        f = open(filename, 'r')
        try:
            content = f.read()
            print("---")
            print(content, end="")
            print("---")
        finally:
            f.close()
        print(f"File '{filename}' closed.")
    except OSError as e:
        print(f"Error opening file '{filename}': {e}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: ft_ancient_text.py <file>")
        return
    display_file(sys.argv[1])


if __name__ == "__main__":
    main()
