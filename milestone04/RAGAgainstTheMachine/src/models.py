"""データモデル: 段階の間で受け渡すデータの形（pydantic が検査する）。"""

import uuid

from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """コーパス内の場所: ファイルと文字範囲（text[first:last]）。

    チャンクもこの形で持つ。本文は保存しない。
    """

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """答えのない質問。"""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """正解（答えと、答えがある場所）つきの質問。"""

    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """質問のデータセット。"""

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """1 つの質問の検索結果（良い順）。"""

    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """検索結果に、回答を足したもの。"""

    answer: str


class StudentSearchResults(BaseModel):
    """search_dataset の出力ファイル。"""

    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """answer_dataset の出力ファイル。"""

    search_results: list[MinimalAnswer]
    k: int


class SearchIndex(BaseModel):
    """index コマンドが保存する、検索に必要なもの全部。"""

    # チャンクの場所。チャンク番号はこのリストの位置。
    chunks: list[MinimalSource]
    # 転置インデックス: 単語 -> [(チャンク番号, 出現回数), ...]
    postings: dict[str, list[tuple[int, int]]]
    # 各チャンクのトークン数と、その平均（BM25 の長さ補正に使う）。
    chunk_lengths: list[int]
    average_chunk_length: float
    # 検索結果の点数にかける係数（チャンク番号順）。tests や examples の
    # チャンクは 1 より小さくして、少しだけ順位を下げる。
    chunk_weights: list[float] = Field(default_factory=list)
    # ファイルの指紋: 中身が同じファイルを、次の index で読み直さないため。
    file_digests: dict[str, str] = Field(default_factory=dict)


class IndexUpdate(BaseModel):
    """index コマンドが何をしたか: 新しい index と、前の index との関係。"""

    index: SearchIndex
    # 読み直したファイルと、なくなったファイル。
    changed_files: list[str]
    removed_files: list[str]
