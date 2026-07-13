#!/usr/bin/env python3


def secure_archive(
    filename: str,
    action: int | str | None = None,
    content: str = "",
) -> tuple[bool, str]:
    mode = "w" if action in (1, "write") else "r"
    try:
        with open(filename, mode) as f:
            if mode == "r":
                return (True, f.read())
            f.write(content)
            return (True, "Content successfully written to file")
    except OSError as e:
        return (False, f"[Errno {e.errno}] {e.strerror}: '{e.filename}'")


def main() -> None:
    print("=== Cyber Archives Security ===")

    print("\nUsing 'secure_archive' to read from a nonexistent file:")
    print(secure_archive("/not/existing/file"))

    print("\nUsing 'secure_archive' to read from an inaccessible file:")
    print(secure_archive("/etc/master.passwd"))

    print("\nUsing 'secure_archive' to read from a regular file:")
    read_result = secure_archive("ancient_fragment.txt")
    print(read_result)

    print("\nUsing 'secure_archive' to write previous content to a new file:")
    if read_result[0]:
        print(secure_archive("new_archive.txt", "write", read_result[1]))


if __name__ == "__main__":
    main()
