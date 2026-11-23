"""差分インデックスのテスト: 変わったファイルだけを読み直す。"""

from pathlib import Path

import pytest

from src.indexing import update_index


@pytest.fixture
def raw(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """3 つのファイルのコーパスを作り、そのフォルダに移る。"""
    monkeypatch.chdir(tmp_path)
    folder = tmp_path / "data" / "raw"
    folder.mkdir(parents=True)
    (folder / "guide.md").write_text(
        "# LoRA\n\nLoRA adapters are loaded at startup.\n", encoding="utf-8"
    )
    (folder / "scheduler.py").write_text(
        "def schedule(requests):\n    return sorted(requests)\n",
        encoding="utf-8",
    )
    (folder / "notes.txt").write_text("plain notes\n", encoding="utf-8")
    return folder


def test_first_run_reads_every_file(raw: Path) -> None:
    """最初の実行では、全部のファイルを読む。"""
    update = update_index(None, "data/raw", 2000)
    assert len(update.changed_files) == 3
    assert update.removed_files == []


def test_second_run_reuses_every_file(raw: Path) -> None:
    """2 回目の実行では、全部のファイルを使い回す。"""
    first = update_index(None, "data/raw", 2000)
    second = update_index(first.index, "data/raw", 2000)
    assert second.changed_files == []
    assert second.index == first.index


def test_only_the_changed_file_is_read_again(raw: Path) -> None:
    """変わったファイルだけを読み直す。"""
    first = update_index(None, "data/raw", 2000)
    (raw / "guide.md").write_text(
        "# Quantization\n\nFP8 weights are supported.\n", encoding="utf-8"
    )
    second = update_index(first.index, "data/raw", 2000)
    assert second.changed_files == ["data/raw/guide.md"]
    # 変わっていないファイルは、チャンクをそのまま使う。
    kept = [c for c in second.index.chunks if c in first.index.chunks]
    assert len(kept) == len(second.index.chunks) - 1


def test_incremental_index_equals_a_full_rebuild(raw: Path) -> None:
    """差分で作った index は、全部作り直した index と同じになる。"""
    first = update_index(None, "data/raw", 2000)
    (raw / "guide.md").write_text("# New\n\nNew text.\n", encoding="utf-8")
    (raw / "added.md").write_text("# Added\n\nAdded text.\n", encoding="utf-8")
    (raw / "notes.txt").unlink()
    incremental = update_index(first.index, "data/raw", 2000)
    rebuilt = update_index(None, "data/raw", 2000)
    assert incremental.index == rebuilt.index
    assert incremental.removed_files == ["data/raw/notes.txt"]
    assert sorted(incremental.changed_files) == [
        "data/raw/added.md", "data/raw/guide.md",
    ]


def test_a_different_chunk_size_reads_every_file_again(raw: Path) -> None:
    """max_chunk_size が違えば、全部のファイルを読み直す。"""
    first = update_index(None, "data/raw", 2000)
    second = update_index(first.index, "data/raw", 1000)
    assert len(second.changed_files) == 3
