"""インデックス作成: 重い処理（読む・切る・数える）をここで 1 回だけ行う。"""

import hashlib
import re
from collections import Counter
from pathlib import Path

from tqdm import tqdm

from src.chunking import chunk_file
from src.corpus import is_supporting_file, list_corpus_files, read_text
from src.errors import RagError
from src.models import IndexUpdate, MinimalSource, SearchIndex
from src.storage import load_json, save_json
from src.tokenization import tokenize

INDEX_FILE_NAME = "index.json"
VECTORS_FILE_NAME = "vectors.npz"

# ファイルパスの単語もチャンクに足す（PATH_WEIGHT 回）。
# "lora/models.py" のチャンクは、本文に書いてなくても LoRA の話だから。
PATH_WEIGHT = 3

# Markdown の見出しの単語もチャンクに足す（HEADING_WEIGHT 回）。
# 見出しは節の題名なので、本文より内容をよく表す。
HEADING_WEIGHT = 1
MARKDOWN_HEADING_LINE = re.compile(r"^#{1,6} .*$", re.MULTILINE)

# 補助ファイル（tests/ や examples/ など）のチャンクの点数にかける係数。
# 0 にはしない: 補助ファイルに答えがある質問にも答えられるように。
SUPPORTING_FILE_WEIGHT = 0.8

# ドキュメント（.md）のチャンクの点数にかける係数。
# 説明を求める質問の答えはドキュメントにあることが多いのに、
# 同じ単語をたくさん含むコードのチャンクに負けていたから。
MARKDOWN_WEIGHT = 1.2


def count_terms(chunk: MinimalSource, text: str) -> Counter[str]:
    """チャンクが持つ単語と、その出現回数を数える。

    チャンク番号とは無関係。

    Args:
        chunk: チャンクの場所。
        text: チャンクの本文。

    Returns:
        単語ごとの出現回数。
    """
    tokens = tokenize(text) + tokenize(chunk.file_path) * PATH_WEIGHT
    if chunk.file_path.endswith(".md"):
        for heading in MARKDOWN_HEADING_LINE.findall(text):
            tokens += tokenize(heading) * HEADING_WEIGHT
    return Counter(tokens)


def chunk_weight(file_path: str) -> float:
    """ファイルの種類によって、チャンクの点数にかける係数を返す。

    Args:
        file_path: チャンクのファイルパス。

    Returns:
        補助ファイルなら 0.8 倍、.md なら 1.2 倍（両方なら両方かける）。
    """
    weight = 1.0
    if is_supporting_file(file_path):
        weight *= SUPPORTING_FILE_WEIGHT
    if file_path.endswith(".md"):
        weight *= MARKDOWN_WEIGHT
    return weight


def assemble_index(
    chunks: list[MinimalSource],
    term_counts: list[Counter[str]],
    file_digests: dict[str, str],
) -> SearchIndex:
    """転置インデックスを作る: 単語 -> [(チャンク番号, 出現回数), ...]

    Args:
        chunks: チャンクの場所（チャンク番号はこのリストの位置）。
        term_counts: チャンクごとの単語の数。
        file_digests: ファイルごとの指紋。

    Returns:
        検索に必要なものをまとめた index。
    """
    postings: dict[str, list[tuple[int, int]]] = {}
    chunk_lengths: list[int] = []
    for chunk_id, counts in enumerate(term_counts):
        chunk_lengths.append(sum(counts.values()))
        for token, occurrences in counts.items():
            postings.setdefault(token, []).append((chunk_id, occurrences))
    average = sum(chunk_lengths) / len(chunk_lengths) if chunks else 0.0
    return SearchIndex(
        chunks=chunks,
        postings=postings,
        chunk_lengths=chunk_lengths,
        average_chunk_length=average,
        chunk_weights=[chunk_weight(chunk.file_path) for chunk in chunks],
        file_digests=file_digests,
    )


# --- 差分インデックス: 変わったファイルだけ作り直す ---
# ファイルの指紋。中身と max_chunk_size が同じなら、チャンクも同じになる。
# 切り方や単語の数え方を変えたら、INDEXING_VERSION を上げること
# （上げないと、古い結果を使い回してしまう）。
INDEXING_VERSION = "3"


def file_digest(text: str, max_chunk_size: int) -> str:
    """ファイルの指紋を返す。

    中身と max_chunk_size が同じなら、チャンクも同じになる。

    Args:
        text: ファイルの中身。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        SHA-256 の 16 進数。
    """
    content = f"{INDEXING_VERSION}\n{max_chunk_size}\n{text}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def previous_term_counts(index: SearchIndex) -> list[Counter[str]]:
    """転置インデックスを逆に引いて、チャンクごとの単語の数に戻す。

    Args:
        index: 前の index。

    Returns:
        チャンクごとの単語の数。
    """
    counts: list[Counter[str]] = [Counter() for _ in index.chunks]
    for token, postings in index.postings.items():
        for chunk_id, occurrences in postings:
            counts[chunk_id][token] = occurrences
    return counts


def update_index(
    previous: SearchIndex | None, raw_directory: str, max_chunk_size: int,
) -> IndexUpdate:
    """前の index を使い回して、新しい index を作る。

    previous の中身が同じファイルは、チャンクと単語の数をそのまま使う。
    新しい index は、全部作り直したものと必ず同じになる。

    Args:
        previous: 前の index（なければ None）。
        raw_directory: コーパスのフォルダ。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        新しい index と、前の index との関係。

    Raises:
        RagError: フォルダがない、または対象のファイルがないとき。
    """
    if not Path(raw_directory).is_dir():
        raise RagError(
            f"directory not found: {raw_directory} "
            f"(the vLLM repository goes in data/raw/vllm-0.10.1)"
        )
    file_paths = list_corpus_files(raw_directory)
    if not file_paths:
        raise RagError(f"no .py, .md or .txt file under {raw_directory}")

    previous = previous or assemble_index([], [], {})
    old_counts = previous_term_counts(previous)
    old_chunk_ids: dict[str, list[int]] = {}
    for chunk_id, chunk in enumerate(previous.chunks):
        old_chunk_ids.setdefault(chunk.file_path, []).append(chunk_id)

    chunks: list[MinimalSource] = []
    term_counts: list[Counter[str]] = []
    file_digests: dict[str, str] = {}
    changed_files: list[str] = []
    for file_path in tqdm(file_paths, desc="Indexing", unit="file"):
        text = read_text(file_path)
        if text is None:
            continue
        digest = file_digest(text, max_chunk_size)
        file_digests[file_path] = digest
        if previous.file_digests.get(file_path) == digest:
            for chunk_id in old_chunk_ids.get(file_path, []):
                chunks.append(previous.chunks[chunk_id])
                term_counts.append(old_counts[chunk_id])
            continue
        changed_files.append(file_path)
        for chunk in chunk_file(file_path, text, max_chunk_size):
            chunks.append(chunk)
            term_counts.append(count_terms(
                chunk,
                text[chunk.first_character_index:chunk.last_character_index],
            ))
    return IndexUpdate(
        index=assemble_index(chunks, term_counts, file_digests),
        changed_files=changed_files,
        removed_files=sorted(set(previous.file_digests) - set(file_digests)),
    )


def save_index(index: SearchIndex, processed_directory: str) -> Path:
    """index を JSON ファイルに保存する。

    Args:
        index: 保存する index。
        processed_directory: 保存先のフォルダ。

    Returns:
        書いたファイルのパス。
    """
    path = Path(processed_directory) / INDEX_FILE_NAME
    save_json(index, path, indent=None)
    return path


def load_index(processed_directory: str) -> SearchIndex:
    """保存した index を読む。

    Args:
        processed_directory: index のフォルダ。

    Returns:
        index。

    Raises:
        RagError: index がない、または壊れているとき。
    """
    path = Path(processed_directory) / INDEX_FILE_NAME
    if not path.is_file():
        raise RagError(
            f"no index under {processed_directory}: "
            f"run the index command first"
        )
    return load_json(str(path), SearchIndex)
