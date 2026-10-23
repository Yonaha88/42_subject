"""Map token ids to the text they stand for."""

import json
from pathlib import Path


def byte_to_char() -> dict[int, str]:
    """Give the byte-to-character table of the byte-level BPE.

    Printable bytes stand for themselves; the others are moved to
    unused code points above 255.

    Returns:
        The character that stands for each byte from 0 to 255.
    """
    kept = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    table: dict[int, str] = {}
    extra = 0
    for byte in range(256):
        if byte in kept:
            table[byte] = chr(byte)
        else:
            table[byte] = chr(256 + extra)
            extra += 1
    return table


def load_vocabulary(vocab_path: str) -> dict[int, str]:
    """Read the vocabulary file of the model.

    Args:
        vocab_path: The JSON file that maps tokens to ids.

    Returns:
        The text of each token id. A token that is not valid UTF-8 on
        its own is left out.
    """
    char_to_byte = {char: byte for byte, char in byte_to_char().items()}
    with Path(vocab_path).open(encoding="utf-8") as file:
        raw: dict[str, int] = json.load(file)
    vocabulary: dict[int, str] = {}
    for token, token_id in raw.items():
        try:
            data = bytes(char_to_byte[char] for char in token)
            vocabulary[token_id] = data.decode("utf-8")
        except (KeyError, UnicodeDecodeError):
            continue
    return vocabulary
