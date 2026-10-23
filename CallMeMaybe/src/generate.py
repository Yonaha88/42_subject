"""Constrained decoding: the model writes only what the grammar allows."""

import json
import string
from typing import Any

import numpy as np
from llm_sdk import Small_LLM_Model

from src.grammar import State, allowed_chars, build_grammar, consume
from src.parser import FunctionDefinition
from src.prompt import build_prompt
from src.vocabulary import load_vocabulary

MAX_STEPS = 300


class GenerationError(Exception):
    """The model could not complete a valid function call."""


class FunctionCaller:
    """Turn a request into a function call.

    The model is asked for one token at a time, and only a token that
    the grammar accepts can be chosen.
    """

    def __init__(
        self, model: Small_LLM_Model, functions: list[FunctionDefinition],
    ) -> None:
        """Prepare the vocabulary and the grammar.

        Args:
            model: The language model.
            functions: The functions the model may call.
        """
        self.model = model
        self.functions = {function.name: function for function in functions}
        self.vocabulary = load_vocabulary(model.get_path_to_vocab_file())
        self.grammar = build_grammar(functions)
        names = "".join(
            function.name + "".join(function.parameters)
            for function in functions
        )
        self.alphabet = string.printable + "".join(sorted(set(names)))

    def call(self, request: str) -> dict[str, Any]:
        """Choose a function and its arguments for a request.

        Args:
            request: The user's natural-language request.

        Returns:
            The function name and its parameters, typed as defined.

        Raises:
            GenerationError: If no valid call could be written.
        """
        context = build_prompt(list(self.functions.values()), request)
        data = json.loads(self._write(context))
        function = self.functions[data["name"]]
        parameters = {
            name: _convert(data["parameters"][name], spec.type)
            for name, spec in function.parameters.items()
        }
        return {"name": function.name, "parameters": parameters}

    def _write(self, context: str) -> str:
        """Write a complete function call as JSON text.

        A character that is the only one allowed is written without asking
        the model.
        """
        state = self.grammar
        text = ""
        for _ in range(MAX_STEPS):
            chars = allowed_chars(state, self.alphabet)
            if not chars:
                if state.can_finish():
                    return text
                raise GenerationError(f"dead end after {text!r}")
            if len(chars) == 1:
                piece = chars[0]
                nxt = consume(state, piece)
            else:
                piece, nxt = self._pick_token(context + text, state)
            if nxt is None:
                raise GenerationError(f"dead end after {text!r}")
            text += piece
            state = nxt
        raise GenerationError(f"no end after {MAX_STEPS} steps: {text!r}")

    def _pick_token(self, text: str, state: State) -> tuple[str, State]:
        """Pick the likeliest token that the grammar accepts.

        A leading space that the grammar refuses is dropped from the token.

        Args:
            text: Everything written so far, prompt included.
            state: The current state of the grammar.

        Returns:
            The token and the state after it.

        Raises:
            GenerationError: If no token is accepted.
        """
        ids = self.model.encode(text)[0].tolist()
        logits = np.array(self.model.get_logits_from_input_ids(ids))
        for token_id in np.argsort(-logits):
            token = self.vocabulary.get(int(token_id))
            if not token:
                continue
            nxt = consume(state, token)
            if nxt is None and token[0] == " " and state.feed(" ") is None:
                token = token[1:]
                nxt = consume(state, token) if token else None
            if nxt is not None:
                return token, nxt
        raise GenerationError(f"no token fits after {text[-40:]!r}")


def _convert(value: Any, json_type: str) -> Any:
    """Give a value the Python type of its JSON type (float or int)."""
    if json_type == "number":
        return float(value)
    if json_type == "integer":
        return int(value)
    return value
