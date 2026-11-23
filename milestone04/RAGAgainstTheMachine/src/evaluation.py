"""評価: recall@k = 正解ソースのうち、上位 k 件で見つかった割合。"""

from src.models import (
    AnsweredQuestion, MinimalSource, RagDataset, StudentSearchResults,
)

# 正解と少しでも重なれば「見つけた」とみなす（切り方が違うため）。
MINIMUM_OVERLAP = 0.05


def overlap_ratio(first: MinimalSource, second: MinimalSource) -> float:
    """2 つのソースの重なりの割合（IoU）を返す。

    IoU = 重なる部分の長さ / 両方を合わせた長さ。別ファイルなら 0。

    Args:
        first: 1 つ目のソース。
        second: 2 つ目のソース。

    Returns:
        0 から 1 の値。
    """
    if first.file_path != second.file_path:
        return 0.0
    shared = (
        min(first.last_character_index, second.last_character_index)
        - max(first.first_character_index, second.first_character_index)
    )
    if shared <= 0:
        return 0.0
    covered = (
        first.last_character_index - first.first_character_index
        + second.last_character_index - second.first_character_index
        - shared
    )
    return shared / covered


def question_recall(
    expected: list[MinimalSource], retrieved: list[MinimalSource],
) -> float:
    """1 つの質問の recall を返す。

    Args:
        expected: 正解のソース。
        retrieved: 検索で見つかったソース。

    Returns:
        正解のうち、見つかったものの割合。
    """
    found = 0
    for source in expected:
        if any(
            overlap_ratio(source, result) > MINIMUM_OVERLAP
            for result in retrieved
        ):
            found += 1
    return found / len(expected)


def answered_questions(dataset: RagDataset) -> list[AnsweredQuestion]:
    """正解ソースを持つ質問だけ残す。"""
    return [
        question for question in dataset.rag_questions
        if isinstance(question, AnsweredQuestion) and question.sources
    ]


def recall_at_k(
    dataset: RagDataset, results: StudentSearchResults, k: int,
) -> float:
    """全質問の recall@k の平均を返す。

    Args:
        dataset: 正解つきのデータセット。
        results: 検索結果。
        k: 上位何件まで見るか。

    Returns:
        recall の平均。評価できる質問がなければ 0。
    """
    retrieved_by_question = {
        result.question_id: result.retrieved_sources
        for result in results.search_results
    }
    recalls = []
    for question in answered_questions(dataset):
        retrieved = retrieved_by_question.get(question.question_id, [])
        recalls.append(question_recall(question.sources, retrieved[:k]))
    if not recalls:
        return 0.0
    return sum(recalls) / len(recalls)
