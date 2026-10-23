"""Command-line arguments and input files, validated by pydantic."""

import argparse
import json
from pathlib import Path
from typing import Literal, TypeVar

from pydantic import (
    BaseModel, ConfigDict, Field, TypeAdapter, ValidationError,
    field_validator,
)

DEFAULT_FUNCTIONS = Path("data/input/functions_definition.json")
DEFAULT_INPUT = Path("data/input/function_calling_tests.json")
DEFAULT_OUTPUT = Path("data/output/function_calls.json")
MAX_SHOWN_ERRORS = 5

JsonType = Literal[
    "string", "number", "integer", "boolean", "array", "object", "null",
]

T = TypeVar("T")


class InputError(Exception):
    """An input file or a command-line value cannot be used."""


class Commandline(BaseModel):
    """The three file paths given on the command line."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    functions_path: Path = DEFAULT_FUNCTIONS
    input_path: Path = DEFAULT_INPUT
    output_path: Path = DEFAULT_OUTPUT

    @classmethod
    def from_argv(cls, argv: list[str]) -> "Commandline":
        """Parse the command-line arguments.

        Args:
            argv: The arguments, without the program name.

        Returns:
            The validated command line.
        """
        parser = argparse.ArgumentParser(
            prog="uv run python -m src",
            description="Translate natural language prompts into "
            "function calls.",
            allow_abbrev=False,
        )
        parser.add_argument(
            "--functions_definition", dest="functions_path", type=Path,
            default=DEFAULT_FUNCTIONS, metavar="FILE",
            help=f"function definitions (default: {DEFAULT_FUNCTIONS})",
        )
        parser.add_argument(
            "--input", dest="input_path", type=Path,
            default=DEFAULT_INPUT, metavar="FILE",
            help=f"prompts to process (default: {DEFAULT_INPUT})",
        )
        parser.add_argument(
            "--output", dest="output_path", type=Path,
            default=DEFAULT_OUTPUT, metavar="FILE",
            help=f"file to write the results to (default: {DEFAULT_OUTPUT})",
        )
        args = parser.parse_args(argv)
        return cls(
            functions_path=args.functions_path,
            input_path=args.input_path, output_path=args.output_path,
        )


class TypeSpec(BaseModel):
    """The type of a parameter or of a return value."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    type: JsonType
    description: str | None = None


class FunctionDefinition(BaseModel):
    """A function the model may call, with its typed parameters."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    name: str = Field(min_length=1)
    description: str
    parameters: dict[str, TypeSpec]
    returns: TypeSpec

    @field_validator("parameters")
    @classmethod
    def _check_parameter_names(
        cls, value: dict[str, TypeSpec],
    ) -> dict[str, TypeSpec]:
        """Reject an empty parameter name."""
        if "" in value:
            raise ValueError("parameter names must not be empty")
        return value


class PromptEntry(BaseModel):
    """One natural-language request."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    prompt: str


FUNCTIONS_ADAPTER = TypeAdapter(list[FunctionDefinition])
PROMPTS_ADAPTER = TypeAdapter(list[PromptEntry])


def load_function_definitions(path: Path) -> list[FunctionDefinition]:
    """Read and validate the function definitions file.

    Args:
        path: The JSON file to read.

    Returns:
        The function definitions, in file order.

    Raises:
        InputError: If the file is missing, unreadable or invalid.
    """
    return _validate(
        FUNCTIONS_ADAPTER, _read_json(path), path, "function definitions",
    )


def load_prompts(path: Path) -> list[str]:
    """Read and validate the prompts file.

    Args:
        path: The JSON file to read.

    Returns:
        The prompt texts, in file order.

    Raises:
        InputError: If the file is missing, unreadable or invalid.
    """
    entries = _validate(PROMPTS_ADAPTER, _read_json(path), path, "prompts")
    return [entry.prompt for entry in entries]


def _read_json(path: Path) -> object:
    """Read a UTF-8 JSON file, turning every failure into InputError."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as error:
        raise InputError(f"{path}: no such file") from error
    except OSError as error:
        raise InputError(
            f"{path}: cannot read the file ({error.strerror})"
        ) from error
    except UnicodeDecodeError as error:
        raise InputError(f"{path}: not a UTF-8 text file") from error
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise InputError(
            f"{path}: invalid JSON at line {error.lineno}, column "
            f"{error.colno}: {error.msg}"
        ) from error
    except RecursionError as error:
        raise InputError(f"{path}: the JSON is nested too deeply") from error


def _validate(
    adapter: TypeAdapter[list[T]], data: object, path: Path, what: str,
) -> list[T]:
    """Check that data is a non-empty list that the adapter accepts."""
    if not isinstance(data, list):
        raise InputError(
            f"{path}: expected a JSON array of {what}, got "
            f"{type(data).__name__}"
        )
    if not data:
        raise InputError(f"{path}: the array is empty, no {what} given")
    try:
        return adapter.validate_python(data)
    except ValidationError as error:
        raise InputError(
            f"{path}: invalid {what}\n{_format_errors(error)}"
        ) from error


def _format_errors(error: ValidationError) -> str:
    """List the first validation errors, one per line."""
    details = error.errors()
    lines = [
        f"  {_location(detail['loc'])}: {detail['msg']}"
        for detail in details[:MAX_SHOWN_ERRORS]
    ]
    if len(details) > MAX_SHOWN_ERRORS:
        lines.append(f"  ... and {len(details) - MAX_SHOWN_ERRORS} more")
    return "\n".join(lines)


def _location(loc: tuple[int | str, ...]) -> str:
    """Write an error location such as "[0].parameters.a.type"."""
    text = "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in loc
    )
    return text.lstrip(".") or "top level"
