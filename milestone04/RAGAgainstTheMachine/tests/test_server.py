"""ローカル HTTP API のテスト。小さなコーパスと、偽の回答役を使う。"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.cli import RagCli
from src.models import MinimalSource
from src.searcher import Searcher
from src.server import create_app


class FakeGenerator:
    """モデルなしで答え、呼ばれた回数を数える。"""

    def __init__(self) -> None:
        """呼ばれた回数を 0 にする。"""
        self.calls = 0

    def answer(
        self, question: str, sources: list[MinimalSource],
        max_context_tokens: int,
    ) -> str:
        """決まった形の回答を返す。"""
        self.calls += 1
        return f"answer to {question}"


@pytest.fixture
def api(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> tuple[TestClient, FakeGenerator]:
    """小さなコーパスの index を作り、API を呼べるクライアントを返す。"""
    monkeypatch.chdir(tmp_path)
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "guide.md").write_text(
        "# LoRA\n\nLoRA adapters are loaded at startup.\n", encoding="utf-8"
    )
    RagCli().index()
    generator = FakeGenerator()
    app = create_app(
        Searcher("data/processed", use_cache=True), lambda: generator, 2000
    )
    return TestClient(app), generator


def test_the_root_page_goes_to_the_docs(
    api: tuple[TestClient, FakeGenerator],
) -> None:
    """/ を開くと、説明ページ（/docs）に移る。"""
    client, _ = api
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"
    assert client.get("/docs").status_code == 200


def test_health(api: tuple[TestClient, FakeGenerator]) -> None:
    """/health は、動いていることを返す。"""
    client, _ = api
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "chunks": 1, "method": "bm25"}


def test_search(api: tuple[TestClient, FakeGenerator]) -> None:
    """/search は、検索結果を返す。"""
    client, _ = api
    response = client.get("/search?query=LoRA%20adapters&k=3")
    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "LoRA adapters"
    assert body["retrieved_sources"][0]["file_path"] == "data/raw/guide.md"


def test_answer_by_post_and_by_get(
    api: tuple[TestClient, FakeGenerator],
) -> None:
    """/answer は、POST でも GET でも答える。"""
    client, _ = api
    response = client.post("/answer", json={"query": "LoRA adapters", "k": 1})
    assert response.status_code == 200
    assert response.json()["answer"] == "answer to LoRA adapters"
    response = client.get("/answer?query=LoRA%20adapters")
    assert response.status_code == 200
    assert response.json()["retrieved_sources"][0]["file_path"] == (
        "data/raw/guide.md"
    )


def test_the_same_answer_is_not_written_twice(
    api: tuple[TestClient, FakeGenerator],
) -> None:
    """同じ質問の回答は、2 回目からキャッシュから返す。"""
    client, generator = api
    for _ in range(3):
        client.post("/answer", json={"query": "LoRA adapters", "k": 1})
    assert generator.calls == 1


def test_wrong_requests_get_a_json_error(
    api: tuple[TestClient, FakeGenerator],
) -> None:
    """正しくない要求には、JSON のエラーを返す。"""
    client, _ = api
    bad_paths = (
        "/search", "/search?query=%20",
        "/search?query=lora&k=0", "/search?query=lora&k=many",
    )
    for path in bad_paths:
        response = client.get(path)
        assert response.status_code == 400
        assert "error" in response.json()
    assert client.get("/nothing").status_code == 404
    headers = {"Content-Type": "application/json"}
    for body in (b"{not json", b"[1, 2]"):
        response = client.post("/answer", content=body, headers=headers)
        assert response.status_code == 400
        assert "error" in response.json()


def test_the_server_keeps_working_after_an_error(
    api: tuple[TestClient, FakeGenerator],
) -> None:
    """エラーのあとも、サーバーは動き続ける。"""
    client, _ = api
    client.get("/search?query=lora&k=0")
    assert client.get("/health").status_code == 200
