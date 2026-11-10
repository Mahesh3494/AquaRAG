import psycopg
import pytest
import requests
from fastapi.testclient import TestClient

import src.api
from src.api import create_app
from src.pipeline import EmptyIndexError

RESULTS = [
    {"text": "pH 7.5 to 8.5", "source_doc": "fao.pdf", "page": 12, "chunk_index": 0, "score": 9.1},
    {"text": "lime the pond", "source_doc": "mpeda.pdf", "page": 27, "chunk_index": 3, "score": 4.2},
]


def fake_ask(question, k):
    return f"answer to {question} with k={k}", RESULTS


client = TestClient(create_app(fake_ask))


def failing_client(error: Exception) -> TestClient:
    """A client whose ask function always raises `error`."""
    def ask_fn(question, k):
        raise error
    return TestClient(create_app(ask_fn))


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ask_returns_answer_with_default_k():
    resp = client.post("/ask", json={"question": "pH?"})
    assert resp.status_code == 200
    assert resp.json()["answer"] == "answer to pH? with k=5"


def test_ask_passes_custom_k():
    resp = client.post("/ask", json={"question": "pH?", "k": 3})
    assert resp.json()["answer"] == "answer to pH? with k=3"


def test_sources_are_numbered_like_the_citations():
    # [1] in the answer means the first result, so n starts at 1.
    resp = client.post("/ask", json={"question": "pH?"})
    assert resp.json()["sources"] == [
        {"n": 1, "source_doc": "fao.pdf", "page": 12},
        {"n": 2, "source_doc": "mpeda.pdf", "page": 27},
    ]


def test_empty_question_is_rejected():
    resp = client.post("/ask", json={"question": "   "})
    assert resp.status_code == 400


def test_missing_question_is_rejected():
    resp = client.post("/ask", json={})
    assert resp.status_code == 422


@pytest.mark.parametrize("k", [0, -1, 21])
def test_k_outside_1_to_20_is_rejected(k):
    resp = client.post("/ask", json={"question": "pH?", "k": k})
    assert resp.status_code == 422


def test_k_of_20_is_allowed():
    resp = client.post("/ask", json={"question": "pH?", "k": 20})
    assert resp.status_code == 200


@pytest.mark.parametrize(
    "error",
    [
        EmptyIndexError("no chunks"),
        requests.Timeout("too slow"),
        requests.ConnectionError("no network"),
        requests.HTTPError("402 Payment Required"),
        psycopg.OperationalError("connection refused"),
    ],
)
def test_a_dependency_failing_gives_503_not_500(error):
    resp = failing_client(error).post("/ask", json={"question": "pH?"})
    assert resp.status_code == 503
    assert resp.json()["detail"]


def test_real_ask_closes_its_connection(monkeypatch):
    class FakeConn:
        closed = False

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.closed = True

    conn = FakeConn()
    monkeypatch.setattr(src.api, "connect", lambda: conn)
    monkeypatch.setattr(src.api, "ask", lambda c, q, k: ("an answer", []))

    src.api.real_ask("pH?", 5)

    assert conn.closed
