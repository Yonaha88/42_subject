#!/usr/bin/env python3

import sys
import os
import site


def main() -> None:
    if sys.prefix == sys.base_prefix:
        print("MATRIX STATUS: You're still plugged in")
        print()
        print(f"Current Python: {sys.executable}")
        print("Virtual Environment: None detected")
        print()
        print("WARNING: You're in the global environment!")
        print("The machines can see everything you install.")
        print()
        print("To enter the construct, run:")
        print("    python -m venv matrix_env")
        print("    source matrix_env/bin/activate  # On Unix")
        print("    matrix_env\\Scripts\\activate     # On Windows")
        print()
        print("Then run this program again.")
    else:
        venv_path = os.environ.get("VIRTUAL_ENV", "")
        venv_name = os.path.basename(venv_path)
        print("MATRIX STATUS: Welcome to the construct")
        print()
        print(f"Current Python: {sys.executable}")
        print(f"Virtual Environment: {venv_name}")
        print(f"Environment Path: {venv_path}")
        print()
        print("SUCCESS: You're in an isolated environment!")
        print("Safe to install packages without affecting")
        print("the global system.")
        print()
        print("Package installation path:")
        print(site.getsitepackages()[0])


if __name__ == "__main__":
    main()
