"""コーパス: どのファイルを対象にし、どう読むか。"""

import os
from pathlib import Path

from src.models import MinimalSource

INDEXED_EXTENSIONS = {".py", ".md", ".txt"}

# 答えがあるのは主にライブラリ本体（vllm/）とドキュメント（docs/）。
# 次のフォルダの中のファイルは「補助ファイル」として少し順位を下げる。
SUPPORTING_DIRECTORIES = frozenset({
    "tests", "benchmarks", "examples", "tools", "requirements",
    "csrc", "cmake", ".buildkite", ".github",
})


def list_corpus_files(raw_directory: str) -> list[str]:
    """対象のファイルを、パスの順に返す。

    file_path は採点で文字列として比較されるので、
    「data/raw/...」という書き方を変えてはいけない。

    Args:
        raw_directory: コーパスのフォルダ。

    Returns:
        .py、.md、.txt のファイルパスのリスト。
    """
    file_paths = []
    for directory, _, file_names in os.walk(raw_directory):
        for file_name in file_names:
            if Path(file_name).suffix.lower() in INDEXED_EXTENSIONS:
                path = os.path.relpath(os.path.join(directory, file_name))
                file_paths.append(Path(path).as_posix())
    return sorted(file_paths)


def read_text(file_path: str) -> str | None:
    """ファイルを読む。

    ファイルは必ずこの関数で読む（読み方が変わると文字位置がずれる）。

    Args:
        file_path: ファイルのパス。

    Returns:
        ファイルの中身。読めない（UTF-8 でないなど）ときは None。
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            return file.read()
    except (OSError, UnicodeDecodeError):
        return None


def read_source_text(source: MinimalSource) -> str:
    """ソースが指す範囲の文字を返す。

    Args:
        source: ファイルと文字範囲。

    Returns:
        範囲の文字。ファイルがなければ空文字。
    """
    text = read_text(source.file_path)
    if text is None:
        return ""
    first = max(source.first_character_index, 0)
    last = max(source.last_character_index, first)
    return text[first:last]


def is_supporting_file(file_path: str) -> bool:
    """補助ファイル（テスト、サンプル、ベンチマークなど）かどうか。

    Args:
        file_path: ファイルのパス。

    Returns:
        補助フォルダの中のファイルなら True。
    """
    return any(
        part in SUPPORTING_DIRECTORIES
        for part in Path(file_path).parts[:-1]
    )
