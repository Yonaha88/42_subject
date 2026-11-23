"""JSON ファイルの読み書き。"""

from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from src.errors import RagError

Model = TypeVar("Model", bound=BaseModel)


def load_json(path: str, model_class: type[Model]) -> Model:
    """JSON を読み、pydantic モデルの形に合っているか検査する。

    Args:
        path: JSON ファイルのパス。
        model_class: 期待するモデル。

    Returns:
        読み込んだモデル。

    Raises:
        RagError: ファイルがない、読めない、または形が合わないとき。
    """
    if not Path(path).is_file():
        raise RagError(f"file not found: {path}")
    try:
        with open(path, encoding="utf-8") as file:
            return model_class.model_validate_json(file.read())
    except (OSError, UnicodeDecodeError) as error:
        raise RagError(f"cannot read {path}: {error}") from error
    except ValidationError as error:
        first_problem = error.errors()[0]
        raise RagError(
            f"{path} is not a valid {model_class.__name__} file "
            f"({error.error_count()} problems, first one: "
            f"{first_problem['msg']} at {first_problem['loc']})"
        ) from error


def save_json(model: BaseModel, path: Path, indent: int | None = 2) -> None:
    """モデルを JSON に書き出す（フォルダがなければ作る）。

    Args:
        model: 書き出すモデル。
        path: 書き込み先。
        indent: 字下げの幅（None なら 1 行）。

    Raises:
        RagError: 書けないとき。
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(model.model_dump_json(indent=indent))
    except OSError as error:
        raise RagError(f"cannot write {path}: {error}") from error
