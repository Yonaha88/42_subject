"""トークン化: 文章を、検索で照合する単語のリストにする。

チャンクと質問で同じ関数を使う（作り方が違うと一致しない）。
"""

import re

# 単語のかけら。左から順に試す:
#   [a-z][A-Z]+(?![a-z])  小文字 1 字 + 略語の名前: "vLLM", "gRPC"
#                         ("v" + "LLM" に分けると、"llm" という語が
#                          ほぼ全部の質問に入ってしまう)
#   [A-Z]+(?=[A-Z][a-z])  単語にくっついた略語: "HTTPServer" の "HTTP"
#   [A-Z]?[a-z]+          普通の単語: "Server", "server"
#   [A-Z]+                残りの大文字: "use_HTTP" の "HTTP"
#   [0-9]+                数字: "qwen3" の "3"
WORD_PIECE = re.compile(
    r"[a-z][A-Z]+(?![a-z])|[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+"
)

# 内容を表さない単語。ほとんどの質問に出てくるので捨てる。
STOP_WORDS = frozenset(
    "a an and are as at be but by can do does for from how i if in into is "
    "it its of on or s so than that the their them then there these this "
    "to use used using was what when where which who why will with you "
    "your".split()
)


def tokenize(text: str) -> list[str]:
    """文章を、照合に使う単語のリストにする。

    例: "Loading the ModelRunner configs" -> load, model, runner, config

    Args:
        text: 文章。

    Returns:
        小文字にして、ストップワードを除き、語尾を取った単語のリスト。
    """
    tokens = []
    for piece in WORD_PIECE.findall(text):
        word = piece.lower()
        if word not in STOP_WORDS:
            tokens.append(stem(word))
    return tokens


def stem(word: str) -> str:
    """語尾を取る: caches, cached, caching -> cach

    間違うこともあるが、チャンクと質問で同じように間違うので問題ない。

    Args:
        word: 小文字の単語。

    Returns:
        語尾を取った単語。
    """
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    for ending in ("ing", "ed", "e"):
        if len(word) > len(ending) + 2 and word.endswith(ending):
            return word[:-len(ending)]
    return word
