"""Write the results file."""

import json
from pathlib import Path
from typing import Any


class OutputError(Exception):
    """The results file cannot be written."""


def save_results(path: Path, results: list[dict[str, Any]]) -> None:
    """Write the function calls as indented JSON.

    Args:
        path: The file to write; missing folders are created.
        results: The function calls, one dictionary each.

    Raises:
        OutputError: If the file cannot be written.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(results, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise OutputError(
            f"{path}: cannot write the file ({error.strerror})"
        ) from error
