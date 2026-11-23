"""ユーザーが入力した値の検査。CLI と HTTP API で同じ検査を使う。"""

from src.errors import RagError


def positive_integer(name: str, value: object) -> int:
    """正の整数かどうか検査する。

    Fire は入力を変換する: "--k 5" は int、"--k five" は str、
    "--k 2.5" は float、"--k" だけだと True。型ヒントだけでは守れない。

    Args:
        name: エラーメッセージに出す名前。
        value: 検査する値。

    Returns:
        正の整数。

    Raises:
        RagError: 正の整数でないとき。
    """
    # True は Python では int 扱い（True == 1）なので、先に bool を断る。
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise RagError(f"{name} must be a positive integer, got {value!r}")
    return value


def required_text(name: str, value: object) -> str:
    """空でない文字列かどうか検査する。

    Fire は数字だけのクエリを数値に変えるので、str に戻す。

    Args:
        name: エラーメッセージに出す名前。
        value: 検査する値。

    Returns:
        前後の空白を取った文字列。

    Raises:
        RagError: 空のとき。
    """
    if value is None or isinstance(value, bool) or not str(value).strip():
        raise RagError(f"{name} must not be empty")
    # Fire は数字だけのクエリを数値に変えるので、str に戻す。
    return str(value).strip()


def non_negative_number(name: str, value: object) -> float:
    """0 以上の数かどうか検査する。

    Args:
        name: エラーメッセージに出す名前。
        value: 検査する値。

    Returns:
        float にした値。

    Raises:
        RagError: 0 以上の数でないとき。
    """
    if (
        isinstance(value, bool) or not isinstance(value, (int, float))
        or value < 0
    ):
        raise RagError(f"{name} must be a number >= 0, got {value!r}")
    return float(value)
