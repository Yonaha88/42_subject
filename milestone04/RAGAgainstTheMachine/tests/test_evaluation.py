"""recall@k の計算のテスト。"""

import pytest

from src.evaluation import overlap_ratio, question_recall, recall_at_k
from src.models import (
    AnsweredQuestion, MinimalSearchResults, MinimalSource, RagDataset,
    StudentSearchResults, UnansweredQuestion,
)


def source(file_path: str, first: int, last: int) -> MinimalSource:
    """ソースを 1 行で作る。"""
    return MinimalSource(
        file_path=file_path,
        first_character_index=first,
        last_character_index=last,
    )


def test_overlap_ratio() -> None:
    """重なりの割合（IoU）を、正しく計算する。"""
    assert overlap_ratio(source("a", 0, 100), source("a", 0, 100)) == 1.0
    # 重なりは 50 文字、両方を合わせて 150 文字。
    assert overlap_ratio(source("a", 0, 100), source("a", 50, 150)) == (
        pytest.approx(1 / 3)
    )
    assert overlap_ratio(source("a", 0, 100), source("a", 100, 200)) == 0.0
    assert overlap_ratio(source("a", 0, 100), source("b", 0, 100)) == 0.0


def test_question_recall_counts_the_expected_sources_found() -> None:
    """質問の recall は、正解ソースのうち見つかった割合になる。"""
    expected = [source("a", 0, 100), source("b", 0, 100)]
    assert question_recall(expected, [source("a", 10, 110)]) == 0.5
    assert question_recall(
        expected, [source("a", 0, 100), source("b", 0, 90)]
    ) == 1.0
    assert question_recall(expected, []) == 0.0
    # 同じファイルだが、重なりが小さすぎて見つけたことにならない。
    assert question_recall(expected, [source("a", 99, 2000)]) == 0.0


def test_recall_at_k_only_looks_at_the_first_k_results() -> None:
    """recall@k は、上位 k 件だけを見る。"""
    dataset = RagDataset(rag_questions=[
        AnsweredQuestion(
            question_id="1", question="?", answer="!",
            sources=[source("a", 0, 100)],
        ),
        AnsweredQuestion(
            question_id="2", question="?", answer="!",
            sources=[source("b", 0, 100)],
        ),
        # 正解がない質問は、評価しない。
        UnansweredQuestion(question_id="3", question="?"),
    ])
    results = StudentSearchResults(k=2, search_results=[
        MinimalSearchResults(
            question_id="1", question="?",
            retrieved_sources=[source("z", 0, 100), source("a", 0, 100)],
        ),
        # 質問 2 は結果が 1 つもないので、0 点。
    ])
    assert recall_at_k(dataset, results, 1) == 0.0
    assert recall_at_k(dataset, results, 2) == 0.5
