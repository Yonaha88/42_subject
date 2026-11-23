"""チャンク分割のテスト。"""

from src.chunking import chunk_file, chunk_markdown, chunk_python

PYTHON_CODE = '''import os


def first():
    return 1


@decorator
def second():
    return 2


class Thing:
    def method(self):
        return 3
'''

MARKDOWN = """# Title

Introduction.

## Install

```bash
# this is a shell comment, not a heading
pip install vllm
```

## Usage

Run it.
"""


def texts(text: str, spans: list[tuple[int, int]]) -> list[str]:
    """span のリストを、それぞれの文字列にする。"""
    return [text[first:last] for first, last in spans]


def test_chunks_never_exceed_the_limit() -> None:
    """チャンクは、上限の文字数を超えない。"""
    for limit in (10, 40, 2000):
        for chunk in chunk_python(PYTHON_CODE, limit):
            assert chunk[1] - chunk[0] <= limit
        for chunk in chunk_markdown(MARKDOWN, limit):
            assert chunk[1] - chunk[0] <= limit


def test_chunks_cover_the_file_without_gap_or_overlap() -> None:
    """チャンクをつなげると、すき間も重なりもなく元のファイルに戻る。"""
    for limit in (10, 40, 2000):
        assert "".join(
            texts(PYTHON_CODE, chunk_python(PYTHON_CODE, limit))
        ) == PYTHON_CODE
        assert "".join(
            texts(MARKDOWN, chunk_markdown(MARKDOWN, limit))
        ) == MARKDOWN


def test_python_is_cut_between_statements() -> None:
    """Python は、文と文の間で切られる。"""
    chunks = texts(PYTHON_CODE, chunk_python(PYTHON_CODE, 30))
    assert chunks[0].startswith("import os")
    assert any(chunk.startswith("def first") for chunk in chunks)
    # デコレータは、その関数と同じチャンクに入る。
    assert any(chunk.startswith("@decorator\ndef second") for chunk in chunks)


def test_small_python_statements_are_glued_together() -> None:
    """小さい文は、上限に収まるかぎりくっつく。"""
    assert len(chunk_python(PYTHON_CODE, 2000)) == 1


def test_invalid_python_is_still_chunked() -> None:
    """構文エラーの Python ファイルも、チャンクに切れる。"""
    broken = "def broken(:\n    pass\n" * 5
    chunks = chunk_python(broken, 30)
    assert "".join(texts(broken, chunks)) == broken
    assert all(last - first <= 30 for first, last in chunks)


def test_markdown_gives_one_chunk_per_section() -> None:
    """Markdown は、1 節が 1 チャンクになる。"""
    chunks = texts(MARKDOWN, chunk_markdown(MARKDOWN, 2000))
    assert len(chunks) == 3
    assert chunks[0].startswith("# Title")
    assert chunks[1].startswith("## Install")
    assert chunks[2].startswith("## Usage")


def test_heading_inside_a_code_block_is_ignored() -> None:
    """コードブロックの中の「# ...」は、見出しとして扱わない。"""
    chunks = texts(MARKDOWN, chunk_markdown(MARKDOWN, 2000))
    assert not any(chunk.startswith("# this is") for chunk in chunks)


def test_a_line_longer_than_the_limit_is_cut() -> None:
    """上限より長い 1 行は、上限の位置で切る。"""
    line = "x" * 95
    chunks = chunk_markdown(line, 20)
    assert [last - first for first, last in chunks] == [20, 20, 20, 20, 15]


def test_chunk_file_picks_the_strategy_and_keeps_the_path() -> None:
    """拡張子で戦略を選び、ファイルパスはそのまま残す。"""
    chunks = chunk_file("data/raw/guide.md", MARKDOWN, 2000)
    assert len(chunks) == 3
    assert chunks[0].file_path == "data/raw/guide.md"
    assert chunks[0].first_character_index == 0
    assert len(chunk_file("data/raw/code.py", PYTHON_CODE, 2000)) == 1


def test_empty_and_blank_files_give_no_chunk() -> None:
    """空のファイルや空白だけのファイルは、チャンクにならない。"""
    assert chunk_file("empty.py", "", 2000) == []
    assert chunk_file("blank.md", "\n\n   \n", 2000) == []
