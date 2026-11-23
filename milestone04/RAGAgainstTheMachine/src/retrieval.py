"""検索: BM25 でチャンクに点をつける。

  idf: 珍しい単語ほど高い
  K1 : 同じ単語の繰り返しは、だんだん効かなくなる
  B  : 長いチャンクは割り引く
"""

import math

import numpy as np
from numpy.typing import NDArray

from src.models import SearchIndex
from src.tokenization import tokenize

K1 = 1.5
B = 0.75


def bm25_ranking(index: SearchIndex, query: str, count: int) -> list[int]:
    """質問の単語を含むチャンクだけを postings から引いて、点を足していく。

    Args:
        index: 検索する index。
        query: 質問。
        count: 返す件数。

    Returns:
        点の高い順のチャンク番号。
    """
    scores: dict[int, float] = {}
    for token in set(tokenize(query)):
        postings = index.postings.get(token, [])
        if not postings:
            continue
        idf = inverse_document_frequency(len(index.chunks), len(postings))
        for chunk_id, occurrences in postings:
            relative_length = (
                index.chunk_lengths[chunk_id] / index.average_chunk_length
            )
            scores[chunk_id] = scores.get(chunk_id, 0.0) + idf * (
                occurrences * (K1 + 1)
                / (occurrences + K1 * (1 - B + B * relative_length))
            )
    # 補助ファイル（tests/ など）は、点数を少し割り引く。
    if index.chunk_weights:
        for chunk_id in scores:
            scores[chunk_id] *= index.chunk_weights[chunk_id]
    # 同点はチャンク番号順にして、結果が毎回同じになるようにする。
    best = sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))
    return best[:count]


def semantic_ranking(
    vectors: NDArray[np.float32], query_vector: NDArray[np.float32],
    count: int,
) -> list[int]:
    """質問に近い順にチャンク番号を返す（意味検索）。

    ベクトルの長さは 1 なので、内積がそのままコサイン類似度になる。

    Args:
        vectors: チャンクのベクトル（1 チャンク 1 行）。
        query_vector: 質問のベクトル。
        count: 返す件数。

    Returns:
        近い順のチャンク番号。
    """
    similarities = vectors @ query_vector
    best = np.argsort(-similarities)[:count]
    return [int(chunk_id) for chunk_id in best]


# --- ハイブリッド検索: 語句の順位と意味の順位を 1 つにまとめる ---
# RRF (reciprocal rank fusion): 各順位表で 1 位なら 1/2 点、2 位なら 1/3 点…
# を足す。点数ではなく順位だけを使うので、BM25 とコサイン類似度のように
# 点数の大きさが違うものも、そのまま混ぜられる。
# 分母に足す数（RRF_OFFSET）は、よく使われる 60 ではなく 1 にする。
# 60 だと 1 位（1/61）と 10 位（1/70）の差がほとんどなく、意味検索の下位の
# 候補まで BM25 の上位を押しのけていた。1 なら各検索の上位だけが強く効く。
RRF_OFFSET = 1


def fuse_rankings(
    rankings: list[list[int]], weights: list[float],
) -> list[int]:
    """複数の順位表を、RRF で 1 つにまとめる。

    Args:
        rankings: 順位表（チャンク番号の列）のリスト。
        weights: 順位表ごとの重み。

    Returns:
        まとめた順位のチャンク番号。
    """
    scores: dict[int, float] = {}
    for ranking, weight in zip(rankings, weights):
        for position, chunk_id in enumerate(ranking):
            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + weight / (RRF_OFFSET + position + 1)
            )
    return sorted(scores, key=lambda chunk_id: (-scores[chunk_id], chunk_id))


def inverse_document_frequency(
    chunk_count: int, chunks_with_token: int,
) -> float:
    """単語の珍しさを返す。

    含むチャンクが少ないほど大きく、ほぼ全部のチャンクにある単語は 0 に近い。

    Args:
        chunk_count: チャンクの総数。
        chunks_with_token: その単語を含むチャンクの数。

    Returns:
        idf の値。
    """
    return math.log(
        (chunk_count - chunks_with_token + 0.5) / (chunks_with_token + 0.5)
        + 1
    )
