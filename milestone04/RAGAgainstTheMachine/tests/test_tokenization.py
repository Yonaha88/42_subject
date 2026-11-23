"""トークナイザのテスト。"""

from src.tokenization import stem, tokenize


def test_words_are_lowercased() -> None:
    """単語は小文字になる。"""
    assert tokenize("Model RUNNER") == ["model", "runner"]


def test_names_are_split_into_words() -> None:
    """snake_case や CamelCase の名前は、単語に分かれる。"""
    assert tokenize("snake_case_name") == tokenize("snake case name")
    assert tokenize("ModelRunner") == ["model", "runner"]
    assert tokenize("HTTPServer") == ["http", "server"]
    assert tokenize("qwen3") == ["qwen", "3"]


def test_product_names_stay_whole() -> None:
    """"vLLM" は "v" + "llm" に分けず、"vllm" と同じ 1 語にする。"""
    assert tokenize("vLLM") == tokenize("vllm") == ["vllm"]


def test_stop_words_are_dropped() -> None:
    """ストップワードは取り除かれる。"""
    assert tokenize("what is the model") == ["model"]


def test_related_words_give_the_same_token() -> None:
    """同じ語幹の単語は、同じトークンになる。"""
    assert stem("caches") == stem("cached") == stem("caching") == stem("cache")
    assert stem("config") == stem("configs")


def test_short_words_are_left_alone() -> None:
    """短い単語は、語尾を取らない。"""
    assert stem("gpu") == "gpu"
    assert stem("bus") == "bus"
    assert stem("class") == "class"


def test_text_without_any_word_gives_no_token() -> None:
    """単語が 1 つもない文章は、トークンにならない。"""
    assert tokenize("") == []
    assert tokenize("?!... ---") == []
