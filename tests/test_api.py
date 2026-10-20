from fastapi.testclient import TestClient

from src.api import create_app


def fake_ask(question, k):
    return f"answer to {question} with k={k}"


client = TestClient(create_app(fake_ask))


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ask_returns_answer_with_default_k():
    resp = client.post("/ask", json={"question": "pH?"})
    assert resp.status_code == 200
    assert resp.json() == {"answer": "answer to pH? with k=5"}


def test_ask_passes_custom_k():
    resp = client.post("/ask", json={"question": "pH?", "k": 3})
    assert resp.json()["answer"] == "answer to pH? with k=3"


def test_empty_question_is_rejected():
    resp = client.post("/ask", json={"question": "   "})
    assert resp.status_code == 400


def test_missing_question_is_rejected():
    resp = client.post("/ask", json={})
    assert resp.status_code == 422