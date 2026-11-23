"""意味検索: チャンクを数値のベクトルにして、質問に近いものを探す。

BM25 は「同じ単語があるか」で探す。ベクトルは「似た意味か」で探す。
質問の言い回しが本文と違っても、意味が近ければ見つかる。
torch と transformers を使うのは、このファイルと generation.py だけ。
ベクトルは「ファイルの指紋 + 場所」を名前にして保存する。
だから、変わったチャンクのベクトルだけを作り直せる（差分インデックス）。
"""

from pathlib import Path
from typing import Protocol

import numpy as np
import torch
from numpy.typing import NDArray
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer

from src.corpus import read_source_text
from src.errors import RagError
from src.indexing import VECTORS_FILE_NAME
from src.models import MinimalSource, SearchIndex

# 検索用の小さい英語のモデル（bge-small を 3 層に縮めたもの）。
# 層が MiniLM（6 層）の半分なので速く、同じ時間で 2 倍のトークンを読める。
# 比べたモデルと結果は README に表がある。
EMBEDDING_MODEL = "TaylorAI/bge-micro-v2"
# 1 つのチャンクから読むトークン数の上限。
# 時間はトークン数にほぼ比例する（index --semantic: 192 で 152 秒、256 で 209 秒）。
MAX_TOKENS = 256
BATCH_SIZE = 64

Vectors = NDArray[np.float32]


class Embedder(Protocol):
    """文章をベクトルにするもの。TextEmbedder がその 1 つ。

    テストでは、モデルを読み込まない軽い代わりを使う。
    """

    model_name: str

    def embed(self, texts: list[str], description: str = "") -> Vectors:
        """文章のリストを、1 文章 1 行の行列にする。"""
        ...


class TextEmbedder:
    """埋め込みモデルで、文章をベクトルにする。"""

    def __init__(self, model_name: str = EMBEDDING_MODEL) -> None:
        """モデルは 1 回だけ読み込み、全部の文章で使い回す。

        Args:
            model_name: Hugging Face のモデル名。

        Raises:
            RagError: 読み込めないとき。
        """
        self.model_name = model_name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).eval()
        except (OSError, ValueError) as error:
            raise RagError(
                f"cannot load the model {model_name}: {error}"
            ) from error

    def embed(self, texts: list[str], description: str = "") -> Vectors:
        """文章のリストを、1 文章 1 行の行列にする（各行の長さは 1）。

        Args:
            texts: 文章のリスト。
            description: 進捗バーの名前（空なら表示しない）。

        Returns:
            形が (文章の数, ベクトルの長さ) の行列。
        """
        dimension = self.model.config.hidden_size
        vectors = np.zeros((len(texts), dimension), dtype=np.float32)
        # 長さが近い文章を一緒に処理して、パディングの無駄を減らす。
        order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
        batches = range(0, len(order), BATCH_SIZE)
        for start in tqdm(batches, desc=description, disable=not description):
            ids = order[start:start + BATCH_SIZE]
            vectors[ids] = self.embed_batch([texts[i] for i in ids])
        return vectors

    def embed_batch(self, texts: list[str]) -> Vectors:
        """1 バッチの文章を、ベクトルにする。

        文章のベクトルは、各トークンのベクトルの平均（パディングは除く）。

        Args:
            texts: 文章のリスト。

        Returns:
            長さ 1 にそろえたベクトルの行列。
        """
        encoded = self.tokenizer(
            texts, padding=True, truncation=True,
            max_length=MAX_TOKENS, return_tensors="pt",
        )
        with torch.no_grad():
            hidden = self.model(**encoded).last_hidden_state
        # 文章のベクトル = 各トークンのベクトルの平均（パディングは除く）。
        mask = encoded["attention_mask"].unsqueeze(-1).float()
        mean = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
        normalized = torch.nn.functional.normalize(mean, dim=1)
        return np.asarray(normalized.numpy(), dtype=np.float32)


def embedding_text(chunk: MinimalSource) -> str:
    """ベクトルにする文章: ファイルパス + チャンクの本文。

    BM25 と同じで、パスも手がかりになる（"lora/models.py" は LoRA の話）。

    Args:
        chunk: チャンクの場所。

    Returns:
        1 行目がファイルパスの文章。
    """
    return chunk.file_path + "\n" + read_source_text(chunk)


def chunk_key(index: SearchIndex, chunk: MinimalSource) -> str:
    """チャンクのベクトルの名前を返す。

    中身が同じなら、いつでも同じ名前になる。

    Args:
        index: チャンクを持つ index。
        chunk: チャンクの場所。

    Returns:
        ファイルの指紋と場所から作った名前。
    """
    digest = index.file_digests.get(chunk.file_path, "")
    return (
        f"{digest}:{chunk.file_path}:"
        f"{chunk.first_character_index}:{chunk.last_character_index}"
    )


def vector_settings(model_name: str) -> str:
    """ベクトルの作り方を表す文字列。保存したベクトルと一緒に書いておく。

    モデルか MAX_TOKENS が変わると、同じチャンクでもベクトルが変わる。
    そのときは保存済みのベクトルを使わず、全部作り直す。

    Args:
        model_name: モデル名。

    Returns:
        例: "TaylorAI/bge-micro-v2, 256 tokens"
    """
    return f"{model_name}, {MAX_TOKENS} tokens"


def read_stored_vectors(
    processed_directory: str, model_name: str,
) -> dict[str, Vectors]:
    """保存してあるベクトルを読む。

    Args:
        processed_directory: 保存先のフォルダ。
        model_name: モデル名（違うモデルや設定のベクトルは使わない）。

    Returns:
        {名前: ベクトル}。なければ空。

    Raises:
        RagError: ファイルが読めないとき。
    """
    path = Path(processed_directory) / VECTORS_FILE_NAME
    if not path.is_file():
        return {}
    try:
        with np.load(path) as file:
            if str(file["model_name"]) != vector_settings(model_name):
                return {}
            keys = [str(key) for key in file["keys"]]
            vectors = file["vectors"]
    except (OSError, ValueError, KeyError) as error:
        raise RagError(f"cannot read {path}: {error}") from error
    return dict(zip(keys, vectors))


def write_stored_vectors(
    processed_directory: str, model_name: str,
    keys: list[str], vectors: Vectors,
) -> Path:
    """ベクトルを名前つきで保存する。

    Args:
        processed_directory: 保存先のフォルダ。
        model_name: モデル名。
        keys: ベクトルの名前。
        vectors: ベクトルの行列（names と同じ順）。

    Returns:
        書いたファイルのパス。

    Raises:
        RagError: 書けないとき。
    """
    path = Path(processed_directory) / VECTORS_FILE_NAME
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            path, model_name=np.array(vector_settings(model_name)),
            keys=np.array(keys), vectors=vectors,
        )
    except OSError as error:
        raise RagError(f"cannot write {path}: {error}") from error
    return path


def update_vectors(
    index: SearchIndex, processed_directory: str, embedder: Embedder,
) -> tuple[int, int]:
    """index に合わせてベクトルを作る。保存済みのものは作り直さない。

    Args:
        index: ベクトルを作る対象の index。
        processed_directory: 保存先のフォルダ。
        embedder: 文章をベクトルにするもの。

    Returns:
        作ったベクトルの数と、使い回した数。
    """
    stored = read_stored_vectors(processed_directory, embedder.model_name)
    keys = [chunk_key(index, chunk) for chunk in index.chunks]
    missing = [i for i, key in enumerate(keys) if key not in stored]
    if missing:
        texts = [embedding_text(index.chunks[i]) for i in missing]
        created = embedder.embed(texts, "Embedding")
        for i, vector in zip(missing, created):
            stored[keys[i]] = vector
    # index のチャンクの順に並べる（もう使わないチャンクのベクトルは捨てる）。
    vectors = (
        np.stack([stored[key] for key in keys]) if keys
        else np.zeros((0, 0), dtype=np.float32)
    )
    write_stored_vectors(
        processed_directory, embedder.model_name, keys, vectors
    )
    return len(missing), len(keys) - len(missing)


def load_vectors(
    index: SearchIndex, processed_directory: str,
    model_name: str = EMBEDDING_MODEL,
) -> Vectors:
    """検索用に、index のチャンク順にそろえたベクトルの行列を読む。

    Args:
        index: チャンクを持つ index。
        processed_directory: 保存先のフォルダ。
        model_name: モデル名。

    Returns:
        形が (チャンクの数, ベクトルの長さ) の行列。

    Raises:
        RagError: ベクトルがないチャンクがあるとき。
    """
    stored = read_stored_vectors(processed_directory, model_name)
    keys = [chunk_key(index, chunk) for chunk in index.chunks]
    missing = sum(1 for key in keys if key not in stored)
    if missing or not keys:
        raise RagError(
            f"{missing} of {len(keys)} chunks have no vector: "
            f"run the index command with --semantic"
        )
    return np.stack([stored[key] for key in keys])
