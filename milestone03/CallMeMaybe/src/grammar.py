"""Character-level grammar of a function call.

Every state is immutable: feeding a character returns a new state, or None
when the character is not allowed. Several states can then be tried and
dropped without undoing anything.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod

from src.parser import FunctionDefinition

DIGITS = "0123456789"
NONZERO_DIGITS = "123456789"
HEX_DIGITS = "0123456789abcdefABCDEF"
SIMPLE_ESCAPES = '"\\/bfnrt'


class GrammarError(Exception):
    """A function definition cannot be turned into a grammar."""


class State(ABC):
    """A position in the grammar: what has been read so far."""

    @abstractmethod
    def feed(self, char: str) -> State | None:
        """Read one character.

        Args:
            char: The next character.

        Returns:
            The state after the character, or None if it is not allowed.
        """

    @abstractmethod
    def can_finish(self) -> bool:
        """Tell whether the text read so far is complete."""


class Literal(State):
    """A fixed text; position counts the characters already read."""

    def __init__(self, text: str, position: int = 0) -> None:
        self.text = text
        self.position = position

    def feed(self, char: str) -> State | None:
        """Accept the next character of the text."""
        if self.position < len(self.text) and char == self.text[self.position]:
            return Literal(self.text, self.position + 1)
        return None

    def can_finish(self) -> bool:
        """True once the whole text has been read."""
        return self.position == len(self.text)


class Number(State):
    """A JSON number.

    fraction allows a decimal part. The mode tells where the number is:
    start, minus, zero, int, dot (after the point) or frac.
    """

    def __init__(self, fraction: bool, mode: str = "start") -> None:
        self.fraction = fraction
        self.mode = mode

    def feed(self, char: str) -> State | None:
        """Accept a character that continues a valid number."""
        mode = self.mode
        if mode in ("start", "minus"):
            if char == "-" and mode == "start":
                return self._to("minus")
            if char == "0":
                return self._to("zero")
            if char in NONZERO_DIGITS:
                return self._to("int")
        elif mode in ("zero", "int"):
            if char == "." and self.fraction:
                return self._to("dot")
            if char in DIGITS and mode == "int":
                return self._to("int")
        elif char in DIGITS:
            return self._to("frac")
        return None

    def can_finish(self) -> bool:
        """True after an integer part or a decimal part."""
        return self.mode in ("zero", "int", "frac")

    def _to(self, mode: str) -> Number:
        """Return the same number in another mode."""
        return Number(self.fraction, mode)


class String(State):
    """A JSON string, quotes included.

    The mode tells where the string is: open, start (just after the opening
    quote, where a space is refused), body, escape, hex (hex_left digits
    still expected after \\u) or closed.
    """

    def __init__(self, mode: str = "open", hex_left: int = 0) -> None:
        self.mode = mode
        self.hex_left = hex_left

    def feed(self, char: str) -> State | None:
        """Accept a character that continues a valid string."""
        if self.mode == "open":
            return String("start") if char == '"' else None
        if self.mode in ("start", "body"):
            if char == '"':
                return String("closed")
            if char == "\\":
                return String("escape")
            if char == " " and self.mode == "start":
                return None
            return String("body") if ord(char) >= 32 else None
        if self.mode == "escape":
            if char in SIMPLE_ESCAPES:
                return String("body")
            return String("hex", 4) if char == "u" else None
        if self.mode == "hex" and char in HEX_DIGITS:
            if self.hex_left == 1:
                return String("body")
            return String("hex", self.hex_left - 1)
        return None

    def can_finish(self) -> bool:
        """True once the closing quote has been read."""
        return self.mode == "closed"


class Choice(State):
    """Any one of several states.

    A branch that refuses a character is dropped.
    """

    def __init__(self, branches: tuple[State, ...]) -> None:
        self.branches = branches

    def feed(self, char: str) -> State | None:
        """Keep only the branches that accept the character."""
        alive: list[State] = []
        for branch in self.branches:
            nxt = branch.feed(char)
            if nxt is not None:
                alive.append(nxt)
        return Choice(tuple(alive)) if alive else None

    def can_finish(self) -> bool:
        """True if any branch is complete."""
        return any(branch.can_finish() for branch in self.branches)


class Sequence(State):
    """Several states one after the other.

    parts are the initial states, index is the current part and current is
    that part's state so far.
    """

    def __init__(
        self, parts: tuple[State, ...], index: int = 0,
        current: State | None = None,
    ) -> None:
        self.parts = parts
        self.index = index
        self.current = parts[index] if current is None else current

    def feed(self, char: str) -> State | None:
        """Feed the current part, or move on if it is complete."""
        nxt = self.current.feed(char)
        if nxt is not None:
            return Sequence(self.parts, self.index, nxt)
        if self.current.can_finish() and self.index + 1 < len(self.parts):
            following = Sequence(self.parts, self.index + 1)
            return following.feed(char)
        return None

    def can_finish(self) -> bool:
        """True if this part and all the next ones are complete."""
        return self.current.can_finish() and all(
            part.can_finish() for part in self.parts[self.index + 1:]
        )


def consume(state: State, text: str) -> State | None:
    """Feed a whole text to a state.

    Args:
        state: The state to start from.
        text: The characters to read.

    Returns:
        The state after the text, or None if a character is not allowed.
    """
    current: State | None = state
    for char in text:
        if current is None:
            return None
        current = current.feed(char)
    return current


def allowed_chars(state: State, alphabet: str) -> list[str]:
    """List the characters of an alphabet that a state accepts.

    Args:
        state: The current state.
        alphabet: The characters to try.

    Returns:
        The accepted characters, in alphabet order.
    """
    return [char for char in alphabet if state.feed(char) is not None]


def value_state(json_type: str) -> State:
    """Build the state of a value of the given JSON type.

    Args:
        json_type: A type name from the function definitions.

    Returns:
        The state that accepts a value of that type.

    Raises:
        GrammarError: If the type is not supported (array, object).
    """
    if json_type == "number":
        return Number(fraction=True)
    if json_type == "integer":
        return Number(fraction=False)
    if json_type == "string":
        return String()
    if json_type == "boolean":
        return Choice((Literal("true"), Literal("false")))
    if json_type == "null":
        return Literal("null")
    raise GrammarError(f"parameter type {json_type!r} is not supported")


def call_state(function: FunctionDefinition) -> State:
    """Build the state of the call of one function.

    The accepted text is {"name": ..., "parameters": {...}} with the
    function name and the parameter names fixed.

    Args:
        function: The function to call.

    Returns:
        The state that accepts exactly that call.
    """
    parts: list[State] = [Literal(
        '{"name": ' + json.dumps(function.name) + ', "parameters": {'
    )]
    for index, (name, spec) in enumerate(function.parameters.items()):
        if index:
            parts.append(Literal(", "))
        parts.append(Literal(json.dumps(name) + ": "))
        parts.append(value_state(spec.type))
    parts.append(Literal("}}"))
    return Sequence(tuple(parts))


def build_grammar(functions: list[FunctionDefinition]) -> State:
    """Build the state that accepts a call of any of the functions.

    Args:
        functions: The functions the model may call.

    Returns:
        The initial state of the grammar.
    """
    return Choice(tuple(call_state(function) for function in functions))
