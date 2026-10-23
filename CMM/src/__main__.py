"""Command-line entry point: prompts in, function calls out."""

import sys
from typing import Any

from llm_sdk import Small_LLM_Model

from src.generate import FunctionCaller, GenerationError
from src.grammar import GrammarError
from src.parser import (
    Commandline, InputError, load_function_definitions, load_prompts,
)
from src.writer import OutputError, save_results


def main() -> int:
    """Run the whole pipeline.

    Returns:
        The exit status: 0 on success, 1 on an input or output error.
    """
    command = Commandline.from_argv(sys.argv[1:])
    try:
        functions = load_function_definitions(command.functions_path)
        prompts = load_prompts(command.input_path)
        caller = FunctionCaller(Small_LLM_Model(), functions)
    except (InputError, GrammarError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    results: list[dict[str, Any]] = []
    for number, prompt in enumerate(prompts, 1):
        try:
            call = caller.call(prompt)
        except GenerationError as error:
            print(f"Warning: prompt {number} skipped: {error}",
                  file=sys.stderr)
            continue
        results.append({"prompt": prompt, **call})
        print(f"[{number}/{len(prompts)}] {call}")
    try:
        save_results(command.output_path, results)
    except OutputError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except MemoryError:
        print("Error: not enough memory to run the model.", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"Unexpected error: {error!r}", file=sys.stderr)
        sys.exit(1)
