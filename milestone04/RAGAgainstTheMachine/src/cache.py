"""キャッシュ: 同じ質問は、2 回目から検索や生成をやり直さずに答える。

ファイルに保存するので、次に起動したときも使える。
index が変わったら中身を捨てる（古い結果を返さないため）。
"""

import hashlib
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, Field, ValidationError

from src.models import MinimalSource
from src.storage import save_json

Value = TypeVar("Value")

CACHE_FILE_NAME = "query_cache.json"
MAX_ENTRIES = 2000
# 点数の付け方など、検索のやり方を変えたら上げる。
# （上げないと、古いやり方の結果が残る）
RETRIEVAL_VERSION = "2"


class CacheContent(BaseModel):
    """キャッシュファイルの中身。fingerprint が違えば使わない。"""

    fingerprint: str
    searches: dict[str, list[MinimalSource]] = Field(default_factory=dict)
    answers: dict[str, str] = Field(default_factory=dict)


def make_fingerprint(paths: list[Path]) -> str:
    """index とベクトルのファイルの中身から、キャッシュの持ち主を決める。

    Args:
        paths: 指紋に含めるファイル（なければ「なし」として扱う）。

    Returns:
        SHA-256 の 16 進数。
    """
    digest = hashlib.sha256(RETRIEVAL_VERSION.encode("utf-8"))
    for path in paths:
        try:
            digest.update(path.read_bytes())
        except OSError:
            digest.update(b"missing")
    return digest.hexdigest()


class QueryCache:
    """検索結果と回答を覚えておくキャッシュ。"""

    def __init__(self, path: Path, fingerprint: str) -> None:
        """キャッシュファイルがあれば読む。

        読めないファイルや、指紋が違うファイルは、なかったことにする。

        Args:
            path: キャッシュファイルの場所。
            fingerprint: 今の index の指紋。
        """
        self.path = path
        self.content = CacheContent(fingerprint=fingerprint)
        self.changed = False
        # 読めないキャッシュは、なかったことにする（作り直せるから）。
        try:
            loaded = CacheContent.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, ValidationError):
            return
        if loaded.fingerprint == fingerprint:
            self.content = loaded

    def get_search(self, key: str) -> list[MinimalSource] | None:
        """覚えている検索結果を返す（なければ None）。"""
        return self.content.searches.get(key)

    def put_search(self, key: str, sources: list[MinimalSource]) -> None:
        """検索結果を覚える。上限を超えたら古いものを捨てる。"""
        self.content.searches[key] = sources
        drop_oldest(self.content.searches)
        self.changed = True

    def get_answer(self, key: str) -> str | None:
        """覚えている回答を返す（なければ None）。"""
        return self.content.answers.get(key)

    def put_answer(self, key: str, answer: str) -> None:
        """回答を覚える。上限を超えたら古いものを捨てる。"""
        self.content.answers[key] = answer
        drop_oldest(self.content.answers)
        self.changed = True

    def save(self) -> None:
        """変わっていれば、ファイルに書く。"""
        if self.changed:
            save_json(self.content, self.path, indent=None)
            self.changed = False


def drop_oldest(entries: dict[str, Value]) -> None:
    """上限を超えている間、一番古いもの（辞書の先頭）から捨てる。"""
    while len(entries) > MAX_ENTRIES:
        del entries[next(iter(entries))]
