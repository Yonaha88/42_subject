"""コマンドのテスト。一時フォルダに作った小さなコーパスを使う。

answer 系のコマンドは、言語モデルの読み込みが遅いので、ここではテストしない。
"""

from pathlib import Path

import pytest

from src.cli import RagCli
from src.errors import RagError
from src.models import (
    AnsweredQuestion, MinimalSource, RagDataset, StudentSearchResults,
)
from src.storage import load_json, save_json
from src.validation import positive_integer, required_text

GUIDE = "# LoRA\n\nLoRA adapters are loaded at startup.\n"
CODE = "def schedule(requests):\n    return sorted(requests)\n"


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """小さなコーパスの index を作り、そのフォルダに移る。"""
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "guide.md").write_text(GUIDE, encoding="utf-8")
    (raw / "scheduler.py").write_text(CODE, encoding="utf-8")
    (raw / "image.png").write_bytes(b"\x89PNG")
    RagCli().index()
    return tmp_path


def write_dataset(path: Path) -> None:
    """答えが guide.md にある質問 1 つのデータセットを書く。"""
    dataset = RagDataset(rag_questions=[
        AnsweredQuestion(
            question_id="q1",
            question="When are LoRA adapters loaded?",
            answer="At startup.",
            sources=[MinimalSource(
                file_path="data/raw/guide.md",
                first_character_index=0,
                last_character_index=len(GUIDE),
            )],
        ),
    ])
    save_json(dataset, path)


def test_search_prints_the_best_source(
    project: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """search は、一番良いソースを表示する。"""
    RagCli().search("LoRA adapters", k=1)
    assert capsys.readouterr().out == (
        f"1. data/raw/guide.md [0:{len(GUIDE)}]\n"
    )


def test_search_with_unknown_words_prints_no_result(
    project: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """知らない単語だけの質問では、「結果なし」と表示する。"""
    RagCli().search("zzzqqq")
    assert "No result found." in capsys.readouterr().out


def test_search_dataset_then_evaluate(
    project: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """search_dataset の結果を、evaluate で採点できる。"""
    write_dataset(project / "questions.json")
    RagCli().search_dataset("questions.json", k=2, save_directory="out")
    results = load_json("out/questions.json", StudentSearchResults)
    assert results.k == 2
    assert results.search_results[0].question_id == "q1"
    assert results.search_results[0].retrieved_sources[0].file_path == (
        "data/raw/guide.md"
    )

    RagCli().evaluate("out/questions.json", "questions.json")
    assert "Recall@1: 1.000" in capsys.readouterr().out


def test_wrong_values_are_refused(project: Path) -> None:
    """正しくない値は、RagError で断る。"""
    cli = RagCli()
    with pytest.raises(RagError):
        cli.search("")
    with pytest.raises(RagError):
        cli.search("lora", k=0)
    with pytest.raises(RagError):
        cli.index(max_chunk_size=2001)
    with pytest.raises(RagError):
        cli.index(raw_directory="missing")
    with pytest.raises(RagError):
        cli.search("lora", processed_directory="missing")
    with pytest.raises(RagError):
        cli.search_dataset("missing.json", save_directory="out")


def test_index_reuses_the_files_that_did_not_change(
    project: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """index は、変わっていないファイルを読み直さない。"""
    RagCli().index()
    assert "0 files read again, 2 reused, 0 removed" in capsys.readouterr().out
    (project / "data" / "raw" / "guide.md").write_text(
        "# Changed\n\nNew text.\n", encoding="utf-8"
    )
    RagCli().index()
    assert "1 files read again, 1 reused, 0 removed" in capsys.readouterr().out
    RagCli().index(full=True)
    assert "2 files read again, 0 reused, 0 removed" in capsys.readouterr().out


def test_search_with_the_cache(
    project: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    """--use_cache を付けると、結果が保存され、同じ結果が返る。"""
    RagCli().search("LoRA adapters", k=1, use_cache=True)
    first = capsys.readouterr().out
    assert (project / "data" / "processed" / "query_cache.json").is_file()
    RagCli().search("LoRA adapters", k=1, use_cache=True)
    assert capsys.readouterr().out == first


def test_wrong_search_options_are_refused(project: Path) -> None:
    """正しくない検索のオプションは、RagError で断る。"""
    cli = RagCli()
    with pytest.raises(RagError, match="--method"):
        cli.search("lora", method="magic")
    with pytest.raises(RagError, match="--semantic_weight"):
        cli.search("lora", semantic_weight=-1)
    with pytest.raises(RagError, match="--port"):
        cli.serve(port=70000)
    with pytest.raises(RagError, match="--host"):
        cli.serve(host="")


def test_hybrid_search_needs_the_vectors(project: Path) -> None:
    """ベクトルがないと、意味検索はできない。"""
    with pytest.raises(RagError, match="--semantic"):
        RagCli().search("lora", method="semantic")


def test_invalid_json_is_refused(project: Path) -> None:
    """壊れた JSON は、RagError で断る。"""
    (project / "broken.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(RagError):
        RagCli().search_dataset("broken.json", save_directory="out")
    with pytest.raises(RagError):
        RagCli().evaluate("broken.json", "broken.json")


def test_positive_integer() -> None:
    """正の整数だけを受け付ける。"""
    assert positive_integer("--k", 3) == 3
    for wrong in (0, -1, 2.5, "3", True, None):
        with pytest.raises(RagError):
            positive_integer("--k", wrong)


def test_required_text() -> None:
    """空でない文字列だけを受け付ける。"""
    assert required_text("the query", "  hello ") == "hello"
    # Fire は、数字だけのクエリを数値に変える。
    assert required_text("the query", 42) == "42"
    for wrong in ("", "   ", None, True):
        with pytest.raises(RagError):
            required_text("the query", wrong)
