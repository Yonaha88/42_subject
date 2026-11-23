"""キャッシュのテスト。"""

from pathlib import Path

from src.cache import MAX_ENTRIES, QueryCache, make_fingerprint
from src.models import MinimalSource

SOURCE = MinimalSource(
    file_path="guide.md", first_character_index=0, last_character_index=10,
)


def test_a_saved_cache_is_read_by_the_next_run(tmp_path: Path) -> None:
    """保存したキャッシュは、次の実行で読める。"""
    path = tmp_path / "cache.json"
    cache = QueryCache(path, "fingerprint")
    cache.put_search("lora", [SOURCE])
    cache.put_answer("lora", "At startup.")
    cache.save()

    reloaded = QueryCache(path, "fingerprint")
    assert reloaded.get_search("lora") == [SOURCE]
    assert reloaded.get_answer("lora") == "At startup."
    assert reloaded.get_search("other") is None


def test_nothing_is_written_when_nothing_changed(tmp_path: Path) -> None:
    """何も変わっていなければ、ファイルを書かない。"""
    path = tmp_path / "cache.json"
    QueryCache(path, "fingerprint").save()
    assert not path.exists()


def test_a_cache_of_another_index_is_ignored(tmp_path: Path) -> None:
    """別の index のキャッシュは、使わない。"""
    path = tmp_path / "cache.json"
    cache = QueryCache(path, "old index")
    cache.put_search("lora", [SOURCE])
    cache.save()
    assert QueryCache(path, "new index").get_search("lora") is None


def test_a_broken_cache_file_is_ignored(tmp_path: Path) -> None:
    """壊れたキャッシュファイルは、なかったことにする。"""
    path = tmp_path / "cache.json"
    path.write_text("{not json", encoding="utf-8")
    cache = QueryCache(path, "fingerprint")
    assert cache.get_search("lora") is None


def test_the_oldest_entries_are_dropped(tmp_path: Path) -> None:
    """上限を超えたら、古いものから捨てる。"""
    cache = QueryCache(tmp_path / "cache.json", "fingerprint")
    for number in range(MAX_ENTRIES + 5):
        cache.put_search(f"query {number}", [SOURCE])
    assert len(cache.content.searches) == MAX_ENTRIES
    assert cache.get_search("query 0") is None
    assert cache.get_search(f"query {MAX_ENTRIES + 4}") == [SOURCE]


def test_the_fingerprint_follows_the_files(tmp_path: Path) -> None:
    """指紋は、ファイルの中身が変わると変わる。"""
    index = tmp_path / "index.json"
    index.write_text("one", encoding="utf-8")
    before = make_fingerprint([index])
    assert make_fingerprint([index]) == before
    index.write_text("two", encoding="utf-8")
    assert make_fingerprint([index]) != before
    assert make_fingerprint([tmp_path / "missing.json"]) != before
