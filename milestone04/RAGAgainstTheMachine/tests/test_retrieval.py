"""index と BM25 検索のテスト。"""

from src.indexing import assemble_index, chunk_weight, count_terms
from src.models import MinimalSource, SearchIndex
from src.retrieval import bm25_ranking, inverse_document_frequency

TEXTS = [
    "The scheduler decides which request runs next.",
    "LoRA adapters are loaded when the server starts. LoRA is cheap.",
    "The server exposes an HTTP endpoint for each request.",
]


def build_index(chunks: list[MinimalSource], texts: list[str]) -> SearchIndex:
    """ファイルを読まずに、本文から直接 index を作る。"""
    counts = [count_terms(chunk, text) for chunk, text in zip(chunks, texts)]
    return assemble_index(chunks, counts, {})


def search(index: SearchIndex, query: str, k: int) -> list[MinimalSource]:
    """BM25 の上位 k 件を、チャンクの場所で返す。"""
    return [index.chunks[i] for i in bm25_ranking(index, query, k)]


def make_index() -> SearchIndex:
    """3 つのチャンク（ファイルごとに 1 つ）の index を作る。"""
    chunks = [
        MinimalSource(
            file_path=f"file{number}.md",
            first_character_index=0,
            last_character_index=len(text),
        )
        for number, text in enumerate(TEXTS)
    ]
    return build_index(chunks, TEXTS)


def test_the_matching_chunk_comes_first() -> None:
    """質問に合うチャンクが、一番上に来る。"""
    index = make_index()
    assert search(index, "How are LoRA adapters loaded?", 3)[0].file_path == (
        "file1.md"
    )
    assert search(index, "scheduler", 3)[0].file_path == "file0.md"


def test_only_matching_chunks_are_returned() -> None:
    """質問の単語を含むチャンクだけが返る。"""
    results = search(make_index(), "request", 3)
    assert {result.file_path for result in results} == {
        "file0.md", "file2.md",
    }


def test_at_most_k_results_are_returned() -> None:
    """返るのは、多くても k 件。"""
    assert len(search(make_index(), "server request scheduler", 1)) == 1


def test_question_without_known_word_gives_no_result() -> None:
    """知っている単語が 1 つもない質問では、何も返らない。"""
    index = make_index()
    assert search(index, "zzzqqq xxxyyy", 3) == []
    assert search(index, "", 3) == []
    assert search(index, "what is the", 3) == []


def test_the_file_path_is_searchable() -> None:
    """ファイルパスの単語でも検索できる。"""
    chunks = [
        MinimalSource(
            file_path="docs/quantization.md",
            first_character_index=0,
            last_character_index=10,
        ),
        MinimalSource(
            file_path="docs/other.md",
            first_character_index=0,
            last_character_index=10,
        ),
    ]
    index = build_index(chunks, ["some text", "some text"])
    assert search(index, "quantization", 2) == [chunks[0]]


def test_a_rare_token_weighs_more_than_a_common_one() -> None:
    """珍しい単語のほうが、ありふれた単語より重い。"""
    rare = inverse_document_frequency(1000, 2)
    common = inverse_document_frequency(1000, 900)
    assert rare > common > 0


def test_documentation_is_favoured_and_supporting_files_are_not() -> None:
    """.md は 1.2 倍、tests/ などの補助ファイルは 0.8 倍になる。"""
    assert chunk_weight("vllm/config.py") == 1.0
    assert chunk_weight("docs/usage/faq.md") == 1.2
    assert chunk_weight("tests/test_config.py") == 0.8
    assert abs(chunk_weight("examples/README.md") - 0.96) < 1e-9
