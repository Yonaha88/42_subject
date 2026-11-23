"""検索器: index（と、必要ならベクトル）を 1 回だけ読み込んで、何度でも検索する。

  bm25     語句の一致で探す（標準。速い）
  semantic 意味の近さで探す（ベクトルが必要: index --semantic）
  hybrid   上の 2 つの順位を RRF で 1 つにまとめる
"""

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from src.cache import CACHE_FILE_NAME, QueryCache, make_fingerprint
from src.errors import RagError
from src.indexing import INDEX_FILE_NAME, VECTORS_FILE_NAME, load_index
from src.models import MinimalSource
from src.retrieval import (
    bm25_ranking, fuse_rankings, semantic_ranking,
)

if TYPE_CHECKING:
    # torch を読み込むのは遅いので、型の確認のときだけ import する。
    from src.semantic import Embedder, Vectors

METHODS = ("bm25", "semantic", "hybrid")
# hybrid で、それぞれの検索から取ってくる候補の数。
POOL_SIZE = 50
# hybrid で、意味検索の順位にかける重み（語句検索は 1）。
# 0.2〜0.6 ならどれもほぼ同じ recall だった（README に表がある）。
SEMANTIC_WEIGHT = 0.3


class Generator(Protocol):
    """答えを書くもの。AnswerGenerator がその 1 つ。"""

    def answer(
        self, question: str, sources: list[MinimalSource],
        max_context_tokens: int,
    ) -> str:
        """ソースをもとに、質問への回答を書く。"""
        ...


class Searcher:
    """index を読み込んで、質問に合うソースを探す。"""

    def __init__(
        self,
        processed_directory: str,
        method: str = "bm25",
        semantic_weight: float = SEMANTIC_WEIGHT,
        use_cache: bool = False,
        embedder: "Embedder | None" = None,
    ) -> None:
        """index を読み込む。

        Args:
            processed_directory: index の場所。
            method: bm25、semantic、hybrid のどれか。
            semantic_weight: hybrid で、意味検索の順位にかける重み。
            use_cache: True なら、結果をキャッシュする。
            embedder: 質問をベクトルにするもの（なければ必要なときに作る）。

        Raises:
            RagError: method が正しくない、または index がないとき。
        """
        if method not in METHODS:
            raise RagError(
                f"--method must be one of {', '.join(METHODS)}, got {method!r}"
            )
        self.method = method
        self.semantic_weight = semantic_weight
        self.index = load_index(processed_directory)
        self.embedder = embedder
        self.vectors: "Vectors | None" = None
        self.processed_directory = processed_directory
        paths = [Path(processed_directory) / INDEX_FILE_NAME]
        if method != "bm25":
            paths.append(Path(processed_directory) / VECTORS_FILE_NAME)
        self.cache: QueryCache | None = None
        if use_cache:
            self.cache = QueryCache(
                Path(processed_directory) / CACHE_FILE_NAME,
                make_fingerprint(paths),
            )

    def search(self, query: str, k: int) -> list[MinimalSource]:
        """質問に合うソースを返す。

        Args:
            query: 質問。
            k: 返す件数。

        Returns:
            良い順のソース。
        """
        key = f"{self.method}|{self.semantic_weight}|{k}|{query}"
        if self.cache is not None:
            cached = self.cache.get_search(key)
            if cached is not None:
                return cached
        sources = [
            self.index.chunks[chunk_id] for chunk_id in self.ranking(query, k)
        ]
        if self.cache is not None:
            self.cache.put_search(key, sources)
        return sources

    def load_semantic_parts(self) -> "tuple[Embedder, Vectors]":
        """モデルとベクトルを、本当に必要になったときに読み込む。

        キャッシュに答えがある質問では、重い torch を読み込まずに済む。

        Returns:
            埋め込みモデルと、チャンクのベクトル。
        """
        from src.semantic import TextEmbedder, load_vectors
        if self.embedder is None:
            self.embedder = TextEmbedder()
        if self.vectors is None:
            self.vectors = load_vectors(
                self.index, self.processed_directory, self.embedder.model_name
            )
        return self.embedder, self.vectors

    def ranking(self, query: str, k: int) -> list[int]:
        """method に応じて、質問に合うチャンク番号を返す。

        Args:
            query: 質問。
            k: 返す件数。

        Returns:
            良い順のチャンク番号。
        """
        if self.method == "bm25":
            return bm25_ranking(self.index, query, k)
        embedder, vectors = self.load_semantic_parts()
        query_vector = embedder.embed([query])[0]
        semantic = semantic_ranking(vectors, query_vector, POOL_SIZE)
        if self.method == "semantic":
            return semantic[:k]
        lexical = bm25_ranking(self.index, query, POOL_SIZE)
        return fuse_rankings(
            [lexical, semantic], [1.0, self.semantic_weight]
        )[:k]

    def answer(
        self, generator: Generator, query: str, k: int,
        max_context_tokens: int,
    ) -> tuple[list[MinimalSource], str]:
        """検索して、答えを書かせる。同じ質問の答えはキャッシュから返す。

        Args:
            generator: 回答を書くもの。
            query: 質問。
            k: 使うソースの数。
            max_context_tokens: 文脈のトークン数の上限。

        Returns:
            使ったソースと、回答。
        """
        sources = self.search(query, k)
        key = f"{self.method}|{k}|{max_context_tokens}|{query}"
        if self.cache is not None:
            cached = self.cache.get_answer(key)
            if cached is not None:
                return sources, cached
        answer = generator.answer(query, sources, max_context_tokens)
        if self.cache is not None:
            self.cache.put_answer(key, answer)
        return sources, answer

    def save_cache(self) -> None:
        """キャッシュを使っていれば、ファイルに保存する。"""
        if self.cache is not None:
            self.cache.save()
