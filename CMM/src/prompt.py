"""Build the chat prompt that is sent to the model."""

from src.parser import FunctionDefinition

# The prompt is re-read by the model at every step, so a shorter prompt
# directly means a faster run.
INSTRUCTIONS = (
    'Reply with one JSON function call: {"name": ..., "parameters": {...}}. '
    "Pick the best function and copy argument values from the request. "
    "In JSON strings every backslash must be doubled. "
    "Copy string values exactly as written, starting right after the quote "
    "with no extra space. "
)


def describe(function: FunctionDefinition) -> str:
    """Describe a function on one line: name, typed arguments, purpose."""
    arguments = ", ".join(
        f"{name}: {spec.type}" for name, spec in function.parameters.items()
    )
    return f"- {function.name}({arguments}): {function.description}"


def build_prompt(functions: list[FunctionDefinition], request: str) -> str:
    """Build the Qwen chat prompt for one request.

    The prompt ends where the assistant starts to answer, so that the
    model continues with the function call.

    Args:
        functions: The functions the model may call.
        request: The user's natural-language request.

    Returns:
        The prompt text.
    """
    listing = "\n".join(describe(function) for function in functions)
    return (
        "<|im_start|>system\n"
        f"{INSTRUCTIONS}\n\nFunctions:\n{listing}<|im_end|>\n"
        f"<|im_start|>user\n{request}<|im_end|>\n"
        "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    )
