"""拡張: 検索結果をプロンプトに入れる（モデルは vLLM を知らないため）。"""

from collections.abc import Callable

from src.corpus import read_source_text
from src.models import MinimalSource

SYSTEM_PROMPT = (
    "You are an assistant that answers questions about the vLLM project. "
    "Answer using only the sources provided by the user. "
    "If the sources do not contain the answer, say that you do not know. "
    "Answer in a few sentences."
)

# 読めるソースがないときは、モデルを呼ばずにこの文を返す。
NO_CONTEXT_ANSWER = "I could not find any source that answers this question."


def build_context(
    sources: list[MinimalSource],
    count_tokens: Callable[[str], int],
    max_context_tokens: int,
) -> str:
    """ソースを良い順に、トークン数の上限に収まるところまで足す。

    Args:
        sources: 検索で見つかったソース（良い順）。
        count_tokens: 文章のトークン数を数える関数。
        max_context_tokens: 文脈に使えるトークン数の上限。

    Returns:
        プロンプトに入れる文脈。読めるソースがなければ空文字。
    """
    parts: list[str] = []
    remaining_tokens = max_context_tokens
    for source in sources:
        snippet = read_source_text(source).strip()
        if not snippet:
            continue
        part = f"[Source {len(parts) + 1}] {source.file_path}\n{snippet}"
        cost = count_tokens(part)
        if cost > remaining_tokens:
            break
        parts.append(part)
        remaining_tokens -= cost
    return "\n\n".join(parts)


def build_messages(question: str, context: str) -> list[dict[str, str]]:
    """モデルに渡すチャットメッセージを作る。

    Args:
        question: ユーザーの質問。
        context: build_context で作った文脈。

    Returns:
        システムメッセージとユーザーメッセージのリスト。
    """
    user_message = f"Sources:\n\n{context}\n\nQuestion: {question}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
