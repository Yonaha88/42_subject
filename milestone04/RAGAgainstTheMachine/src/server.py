"""ローカル HTTP API（FastAPI）: CLI の代わりに、HTTP で検索と回答を呼べる。

  GET  /                           説明ページ（/docs）に移る
  GET  /health                     動いているか
  GET  /search?query=...&k=5       検索
  GET  /answer?query=...&k=5       回答
  POST /answer  {"query": "...", "k": 5}

要求の形（k が正の整数か、本文が JSON か）は FastAPI が検査する。
エラーは JSON の {"error": ...} で返し、サーバーは止めない。
"""

import functools
import threading
import uuid
from collections.abc import Callable

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from src.errors import RagError
from src.models import MinimalAnswer, MinimalSearchResults
from src.searcher import Generator, Searcher
from src.validation import required_text

DEFAULT_K = 5


class Question(BaseModel):
    """POST /answer の本文。"""

    query: str
    k: int = Field(default=DEFAULT_K, gt=0)


def create_app(
    searcher: Searcher,
    make_generator: Callable[[], Generator],
    max_context_tokens: int,
) -> FastAPI:
    """検索器と回答モデルを使う、HTTP API のアプリを作る。

    Args:
        searcher: 検索器。
        make_generator: 回答モデルを作る関数（最初の /answer で 1 回だけ呼ぶ）。
        max_context_tokens: 文脈のトークン数の上限。

    Returns:
        FastAPI のアプリ。
    """
    app = FastAPI(title="RAG against the machine")
    # 検索器とモデルは、同時に 1 つの要求しか処理しない。
    lock = threading.Lock()
    # モデルは最初の /answer で読み込み、あとは同じものを使う（起動を速くするため）。
    load_generator = functools.cache(make_generator)

    def search(query: str, k: int) -> MinimalSearchResults:
        """検索して、結果を MinimalSearchResults にして返す。

        Args:
            query: 質問（空ならエラー）。
            k: 返す件数。

        Returns:
            検索結果。
        """
        query = required_text("query", query)
        with lock:
            sources = searcher.search(query, k)
            searcher.save_cache()
        return MinimalSearchResults(
            question_id=str(uuid.uuid4()), question=query,
            retrieved_sources=sources,
        )

    def answer(query: str, k: int) -> MinimalAnswer:
        """検索して回答を書き、MinimalAnswer にして返す。

        Args:
            query: 質問（空ならエラー）。
            k: 使うソースの数。

        Returns:
            ソースと回答。
        """
        query = required_text("query", query)
        with lock:
            sources, text = searcher.answer(
                load_generator(), query, k, max_context_tokens
            )
            searcher.save_cache()
        return MinimalAnswer(
            question_id=str(uuid.uuid4()), question=query,
            retrieved_sources=sources, answer=text,
        )

    @app.get("/", include_in_schema=False)
    def index() -> RedirectResponse:
        """/ を開いたら、説明ページ（/docs）に移す。"""
        return RedirectResponse("/docs")

    @app.get("/health")
    def health() -> dict[str, object]:
        """動いていることと、チャンクの数を返す。"""
        return {
            "status": "ok",
            "chunks": len(searcher.index.chunks),
            "method": searcher.method,
        }

    @app.get("/search")
    def get_search(
        query: str, k: int = Query(DEFAULT_K, gt=0),
    ) -> MinimalSearchResults:
        """GET /search: 質問に合うソースを返す。"""
        return search(query, k)

    @app.get("/answer")
    def get_answer(
        query: str, k: int = Query(DEFAULT_K, gt=0),
    ) -> MinimalAnswer:
        """GET /answer: 質問に答える。"""
        return answer(query, k)

    @app.post("/answer")
    def post_answer(question: Question) -> MinimalAnswer:
        """POST /answer: JSON の本文の質問に答える。"""
        return answer(question.query, question.k)

    # エラーは、どれも {"error": ...} の形で返す。
    @app.exception_handler(RagError)
    def rag_error(request: Request, error: RagError) -> JSONResponse:
        """RagError（ユーザーが直せる問題）を、JSON のエラー（400）で返す。"""
        return JSONResponse(status_code=400, content={"error": str(error)})

    @app.exception_handler(RequestValidationError)
    def bad_request(
        request: Request, error: RequestValidationError,
    ) -> JSONResponse:
        """要求の形が正しくないとき、最初の問題を JSON のエラー（400）で返す。"""
        problem = error.errors()[0]
        place = ".".join(str(part) for part in problem["loc"])
        return JSONResponse(
            status_code=400,
            content={"error": f"{place}: {problem['msg']}"},
        )

    return app


def run_server(
    searcher: Searcher,
    make_generator: Callable[[], Generator],
    host: str,
    port: int,
    max_context_tokens: int,
) -> None:
    """Ctrl-C で止めるまで待ち続け、止めたらキャッシュを保存する。

    Args:
        searcher: 検索器。
        make_generator: 回答モデルを作る関数。
        host: 待ち受けるアドレス。
        port: 待ち受けるポート。
        max_context_tokens: 文脈のトークン数の上限。
    """
    app = create_app(searcher, make_generator, max_context_tokens)
    try:
        uvicorn.run(app, host=host, port=port)
    finally:
        searcher.save_cache()
