#!/usr/bin/env python3

import sys


def read_file(filename: str) -> str | None:
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
        return content
    except OSError as e:
        print(f"[STDERR] Error opening file '{filename}': {e}",
              file=sys.stderr)
        return None


def transform_content(content: str) -> str:
    lines = content.splitlines()
    return '\n'.join(line + '#' for line in lines) + '\n'


def save_content(transformed: str, filename: str) -> None:
    try:
        f = open(filename, 'w')
        try:
            f.write(transformed)
        finally:
            f.close()
        print(f"Data saved in file '{filename}'.")
    except OSError as e:
        print(f"[STDERR] Error opening file '{filename}': {e}",
              file=sys.stderr)
        print("Data not saved.")


def main() -> None:
    print("=== Cyber Archives Recovery & Preservation ===")
    if len(sys.argv) != 2:
        print("Usage: ft_stream_management.py <file>")
        return
    content = read_file(sys.argv[1])
    if content is None:
        return
    transformed = transform_content(content)
    print("Transform data:")
    print("---")
    print(transformed, end="")
    print("---")
    sys.stderr.write("Enter new file name (or empty): ")
    sys.stderr.flush()
    new_filename = sys.stdin.readline().rstrip('\n')
    if not new_filename:
        print("Not saving data.")
    else:
        print(f"Saving data to '{new_filename}'")
        save_content(transformed, new_filename)


if __name__ == "__main__":
    main()
