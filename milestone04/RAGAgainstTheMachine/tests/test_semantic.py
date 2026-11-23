"""意味検索のインデックスと、ハイブリッド検索のテスト。

本物のモデルは読み込みが遅いので、軽い代わり（FakeEmbedder）を使う。
単語の数を 32 個の箱に数えて、ベクトルにするだけのもの。
"""

import zlib
from pathlib import Path

import numpy as np
import pytest

from src import semantic
from src.errors import RagError
from src.indexing import save_index, update_index
from src.retrieval import fuse_rankings, semantic_ranking
from src.searcher import Searcher
from src.semantic import (
    Vectors, load_vectors, read_stored_vectors, update_vectors,
)
from src.tokenization import tokenize

DIMENSION = 32


class FakeEmbedder:
    """文章を、単語の数のベクトル（長さ 1）にする。"""

    model_name = "fake"

    def __init__(self) -> None:
        """ベクトルにした文章を、覚えておく入れ物を作る。"""
        self.embedded: list[str] = []

    def embed(self, texts: list[str], description: str = "") -> Vectors:
        """文章のリストを、ベクトルの行列にする。"""
        self.embedded.extend(texts)
        vectors = np.zeros((len(texts), DIMENSION), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in tokenize(text):
                vectors[row, zlib.crc32(word.encode()) % DIMENSION] += 1
            norm = np.linalg.norm(vectors[row])
            if norm > 0:
                vectors[row] /= norm
        return vectors


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """3 つのファイルのコーパスと index を作る（ベクトルはなし）。"""
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "lora.md").write_text(
        "# LoRA\n\nLoRA adapters are loaded when the server starts.\n",
        encoding="utf-8",
    )
    (raw / "scheduler.py").write_text(
        "def schedule(requests):\n    return sorted(requests)\n",
        encoding="utf-8",
    )
    (raw / "quant.md").write_text(
        "# Quantization\n\nFP8 weights use less memory.\n", encoding="utf-8"
    )
    save_index(update_index(None, "data/raw", 2000).index, "data/processed")
    return tmp_path


def test_every_chunk_gets_a_vector(project: Path) -> None:
    """全部のチャンクにベクトルができる。"""
    index = update_index(None, "data/raw", 2000).index
    embedder = FakeEmbedder()
    created, reused = update_vectors(index, "data/processed", embedder)
    assert (created, reused) == (len(index.chunks), 0)
    vectors = load_vectors(index, "data/processed", "fake")
    assert vectors.shape == (len(index.chunks), DIMENSION)


def test_a_second_run_embeds_nothing(project: Path) -> None:
    """2 回目の実行では、何もベクトルにしない。"""
    index = update_index(None, "data/raw", 2000).index
    update_vectors(index, "data/processed", FakeEmbedder())
    embedder = FakeEmbedder()
    created, reused = update_vectors(index, "data/processed", embedder)
    assert (created, reused) == (0, len(index.chunks))
    assert embedder.embedded == []


def test_only_the_changed_file_is_embedded_again(project: Path) -> None:
    """変わったファイルのチャンクだけを、ベクトルにし直す。"""
    first = update_index(None, "data/raw", 2000).index
    update_vectors(first, "data/processed", FakeEmbedder())
    (project / "data" / "raw" / "quant.md").write_text(
        "# Quantization\n\nINT8 weights use less memory.\n", encoding="utf-8"
    )
    second = update_index(first, "data/raw", 2000).index
    embedder = FakeEmbedder()
    created, reused = update_vectors(second, "data/processed", embedder)
    assert created == 1
    assert reused == len(second.chunks) - 1
    assert len(embedder.embedded) == 1
    # ベクトルにする文章は「ファイルパス + 本文」。
    assert embedder.embedded[0].startswith("data/raw/quant.md\n")
    assert "INT8" in embedder.embedded[0]


def test_vectors_of_another_model_are_not_used(project: Path) -> None:
    """別のモデルのベクトルは、使わない。"""
    index = update_index(None, "data/raw", 2000).index
    update_vectors(index, "data/processed", FakeEmbedder())
    assert read_stored_vectors("data/processed", "another model") == {}


def test_missing_vectors_are_reported(project: Path) -> None:
    """ベクトルがないときは、そう伝えて断る。"""
    index = update_index(None, "data/raw", 2000).index
    with pytest.raises(RagError, match="--semantic"):
        load_vectors(index, "data/processed", "fake")


def test_semantic_ranking_puts_the_closest_vector_first() -> None:
    """意味検索は、一番近いベクトルを上に置く。"""
    vectors = np.array([[1, 0], [0, 1], [0.6, 0.8]], dtype=np.float32)
    query = np.array([0, 1], dtype=np.float32)
    assert semantic_ranking(vectors, query, 3) == [1, 2, 0]
    assert semantic_ranking(vectors, query, 1) == [1]


def test_fusing_rankings_rewards_chunks_found_by_both() -> None:
    """RRF は、両方の順位表にあるチャンクを高く評価する。"""
    lexical = [5, 7, 9]
    semantic = [9, 8, 5]
    assert fuse_rankings([lexical, semantic], [1.0, 1.0]) == [5, 9, 7, 8]


def test_the_weight_decides_which_ranking_leads() -> None:
    """重みの大きい順位表が、先頭を決める。"""
    lexical = [1, 2]
    semantic = [3, 4]
    assert fuse_rankings([lexical, semantic], [1.0, 0.1])[0] == 1
    assert fuse_rankings([lexical, semantic], [0.1, 1.0])[0] == 3


def test_searcher_methods_find_the_right_file(project: Path) -> None:
    """どの method でも、正しいファイルが 1 位になる。"""
    index = update_index(None, "data/raw", 2000).index
    embedder = FakeEmbedder()
    update_vectors(index, "data/processed", embedder)
    for method in ("bm25", "semantic", "hybrid"):
        searcher = Searcher(
            "data/processed", method=method, embedder=embedder
        )
        results = searcher.search("When are LoRA adapters loaded?", 1)
        assert results[0].file_path == "data/raw/lora.md", method


def test_semantic_search_finds_what_bm25_cannot(project: Path) -> None:
    """BM25 が何も返さない質問でも、意味検索は近いものを返す。"""
    index = update_index(None, "data/raw", 2000).index
    embedder = FakeEmbedder()
    update_vectors(index, "data/processed", embedder)
    # BM25 は知らない単語では何も返さないが、意味検索は近いものを返す。
    bm25 = Searcher("data/processed", embedder=embedder)
    assert bm25.search("zzzqqq", 3) == []
    semantic = Searcher(
        "data/processed", method="semantic", embedder=embedder
    )
    assert len(semantic.search("zzzqqq", 3)) == 3


def test_a_wrong_method_is_refused(project: Path) -> None:
    """正しくない method は、断る。"""
    with pytest.raises(RagError, match="--method"):
        Searcher("data/processed", method="magic")


def test_cached_searches_do_not_search_again(project: Path) -> None:
    """キャッシュにある検索は、もう一度検索しない。"""
    index = update_index(None, "data/raw", 2000).index
    embedder = FakeEmbedder()
    update_vectors(index, "data/processed", embedder)
    searcher = Searcher(
        "data/processed", method="hybrid", embedder=embedder, use_cache=True
    )
    first = searcher.search("LoRA adapters", 2)
    embedded_before = len(embedder.embedded)
    assert searcher.search("LoRA adapters", 2) == first
    assert len(embedder.embedded) == embedded_before
    searcher.save_cache()
    # 新しい検索器は、保存された結果から始まる。
    again = Searcher(
        "data/processed", method="hybrid", embedder=embedder, use_cache=True
    )
    assert again.search("LoRA adapters", 2) == first
    assert len(embedder.embedded) == embedded_before


def test_vectors_are_made_again_when_max_tokens_changes(
    project: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MAX_TOKENS を変えたら、保存済みのベクトルを使い回さない。"""
    index = update_index(None, "data/raw", 2000).index
    update_vectors(index, "data/processed", FakeEmbedder())
    monkeypatch.setattr(semantic, "MAX_TOKENS", semantic.MAX_TOKENS + 1)
    created, reused = update_vectors(index, "data/processed", FakeEmbedder())
    assert (created, reused) == (len(index.chunks), 0)
