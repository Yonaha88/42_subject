"""チャンク分割: ファイルを上限サイズ以下のかけらに切る。

span (first, last) は text[first:last] のこと。
「切ってよい位置」の決め方が 2 通りある。
  Python   : 文の境目（関数は 1 つにまとめる）
  Markdown : 見出し（1 節 = 1 チャンク）
"""

import ast
import re

from src.models import MinimalSource

Span = tuple[int, int]

HEADING = re.compile(r"#{1,6} ")
BLANK_LINES = re.compile(r"\n\s*\n")
CODE_FENCES = ("```", "~~~")


def chunk_file(
    file_path: str, text: str, max_chunk_size: int,
) -> list[MinimalSource]:
    """拡張子で戦略を選んで、ファイルをチャンクに切る。

    Args:
        file_path: コーパス内のファイルパス。
        text: ファイルの中身。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        チャンクの場所のリスト。空白だけのチャンクは含まない。
    """
    if file_path.endswith(".py"):
        spans = chunk_python(text, max_chunk_size)
    else:
        spans = chunk_markdown(text, max_chunk_size)
    return [
        MinimalSource(
            file_path=file_path,
            first_character_index=first,
            last_character_index=last,
        )
        for first, last in spans
        if text[first:last].strip()
    ]


# --- 戦略 1: Python コード ---
def chunk_python(text: str, max_chunk_size: int) -> list[Span]:
    """戦略 1: Python のコードを、文の境目で切る。

    Args:
        text: Python ファイルの中身。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        チャンクの span のリスト。
    """
    whole_file = (0, len(text))
    return fill_chunks(
        text, whole_file, python_boundaries(text), max_chunk_size
    )


def python_boundaries(text: str) -> list[int]:
    """各文の開始位置を返す。クラスはメンバーごとにも切れるようにする。

    構文エラーのファイルは [] を返す（行の境目で切られる）。

    Args:
        text: Python ファイルの中身。

    Returns:
        切ってよい文字位置のリスト。
    """
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError, RecursionError):
        return []
    # ast がくれるのは行番号なので、行頭の文字位置に変換する表を作る。
    line_starts = [0]
    for position, character in enumerate(text):
        if character == "\n":
            line_starts.append(position + 1)

    boundaries = []
    for statement in tree.body:
        boundaries.append(line_starts[first_line(statement) - 1])
        if isinstance(statement, ast.ClassDef):
            for member in statement.body:
                boundaries.append(line_starts[first_line(member) - 1])
    return boundaries


def first_line(statement: ast.stmt) -> int:
    """文が始まる行を返す。デコレータがあれば、その行から始まるとみなす。

    Args:
        statement: ast の文。

    Returns:
        開始行の番号（1 から数える）。
    """
    line = statement.lineno
    if isinstance(
        statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    ):
        for decorator in statement.decorator_list:
            line = min(line, decorator.lineno)
    return line


# --- 戦略 2: Markdown とテキスト ---
def chunk_markdown(text: str, max_chunk_size: int) -> list[Span]:
    """戦略 2: Markdown とテキストを、見出しで切る。

    長すぎる節だけ、段落（空行）で切る。

    Args:
        text: ファイルの中身。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        チャンクの span のリスト。
    """
    paragraphs = [match.end() for match in BLANK_LINES.finditer(text)]
    whole_file = (0, len(text))
    chunks = []
    for section in cut_at(whole_file, heading_boundaries(text)):
        chunks.extend(fill_chunks(text, section, paragraphs, max_chunk_size))
    return chunks


def heading_boundaries(text: str) -> list[int]:
    """見出し行の開始位置を返す。

    コードブロックの中の「# ...」は見出しではないので飛ばす。

    Args:
        text: Markdown の中身。

    Returns:
        見出し行の文字位置のリスト。
    """
    boundaries = []
    position = 0
    inside_code_block = False
    for line in text.split("\n"):
        if line.lstrip().startswith(CODE_FENCES):
            inside_code_block = not inside_code_block
        elif not inside_code_block and HEADING.match(line):
            boundaries.append(position)
        position += len(line) + 1
    return boundaries


# --- 2 つの戦略に共通の補助関数 ---
def fill_chunks(
    text: str, span: Span, boundaries: list[int], max_chunk_size: int,
) -> list[Span]:
    """境目で切ったブロックを、上限に収まるかぎり隣とくっつける。

    例: 上限 10、ブロックが 4, 3, 6, 2 文字 -> 7 文字と 8 文字のチャンク。

    Args:
        text: ファイルの中身。
        span: 切る範囲。
        boundaries: 切ってよい文字位置。
        max_chunk_size: チャンクの最大文字数。

    Returns:
        チャンクの span のリスト。
    """
    chunks: list[Span] = []
    for block in cut_at(span, boundaries):
        for first, last in cut_long_span(text, block, max_chunk_size):
            if chunks and last - chunks[-1][0] <= max_chunk_size:
                chunks[-1] = (chunks[-1][0], last)
            else:
                chunks.append((first, last))
    return chunks


def cut_at(span: Span, boundaries: list[int]) -> list[Span]:
    """span を、境目の位置で切る。

    例: (0, 9) を 4 で切ると (0, 4), (4, 9)。

    Args:
        span: 切る範囲。
        boundaries: 切る位置（範囲の外のものは無視する）。

    Returns:
        切ったあとの span のリスト。
    """
    first, last = span
    if first >= last:
        return []
    inside = sorted({cut for cut in boundaries if first < cut < last})
    points = [first, *inside, last]
    return list(zip(points, points[1:]))


def cut_long_span(text: str, span: Span, max_chunk_size: int) -> list[Span]:
    """上限を超える span を、できるだけ行末で切る。

    Args:
        text: ファイルの中身。
        span: 切る範囲。
        max_chunk_size: 1 つの span の最大文字数。

    Returns:
        どれも上限以下の span のリスト。
    """
    first, last = span
    pieces = []
    while last - first > max_chunk_size:
        limit = first + max_chunk_size
        line_end = text.rfind("\n", first, limit)
        # 1 行が上限より長いと行末がないので、上限の位置で切る。
        cut = limit if line_end == -1 else line_end + 1
        pieces.append((first, cut))
        first = cut
    pieces.append((first, last))
    return pieces
