"""入口: ``uv run python -m src <command> [options]``。

エラーを捕まえて表示するのは、このファイルだけ。
"""

import sys

from src.errors import RagError


def main() -> None:
    """コマンドを実行する。

    RagError はメッセージだけを表示して終了コード 1、Ctrl-C は終了コード 130、
    想定外のエラーもトレースバックを出さずに終了コード 1 で終わる。
    """
    try:
        # try の中で import する: 読み込み中に Ctrl-C を押されても
        # トレースバックを出さないため。
        import fire

        from src.cli import RagCli
        fire.Fire(RagCli)
    except RagError as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)
    # 想定外のエラーでもトレースバックは出さない。
    except Exception as error:
        print(
            f"Unexpected error: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
