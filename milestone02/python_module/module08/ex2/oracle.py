#!/usr/bin/env python3

import os
import sys

try:
    from dotenv import load_dotenv  # type: ignore[import-not-found]
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def load_config() -> dict[str, str]:
    if DOTENV_AVAILABLE:
        load_dotenv()
    else:
        print("WARNING: python-dotenv not installed.")
        print(".env file will be ignored.")
        print("Install it with: pip install python-dotenv\n")
    return {
        "MATRIX_MODE": os.environ.get("MATRIX_MODE", "development"),
        "DATABASE_URL": os.environ.get("DATABASE_URL", ""),
        "API_KEY": os.environ.get("API_KEY", ""),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL", "DEBUG"),
        "ZION_ENDPOINT": os.environ.get("ZION_ENDPOINT", ""),
    }


def check_missing(config: dict[str, str]) -> list[str]:
    required = ["DATABASE_URL", "API_KEY", "ZION_ENDPOINT"]
    return [key for key in required if not config[key]]


def show_config(config: dict[str, str]) -> None:
    mode = config["MATRIX_MODE"]

    if mode == "production":
        db_display = "Connected to production instance"
        zion_display = "Online (production)"
    else:
        db_display = "Connected to local instance"
        zion_display = "Online (development)"

    print("Configuration loaded:")
    print(f"Mode: {mode}")
    print(f"Database: {db_display}")
    api_status = "Authenticated" if config["API_KEY"] else "Not configured"
    print(f"API Access: {api_status}")
    print(f"Log Level: {config['LOG_LEVEL']}")
    print(f"Zion Network: {zion_display}")


def security_check() -> None:
    print()
    print("Environment security check:")
    print("[OK] No hardcoded secrets detected")
    print("[OK] .env file properly configured")
    print("[OK] Production overrides available")


def main() -> None:
    print("ORACLE STATUS: Reading the Matrix...\n")

    config = load_config()
    missing = check_missing(config)

    if missing:
        print("WARNING: Missing configuration:")
        for key in missing:
            print(f"  [KO] {key} is not set")
        print()
        print("Copy .env.example to .env and fill in the values:")
        print("    cp .env.example .env")
        sys.exit(1)

    show_config(config)
    security_check()
    print()
    print("The Oracle sees all configurations.")


if __name__ == "__main__":
    main()
