"""HTTP API for AquaRAG."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.pipeline import ask
from src.store import connect


class AskRequest(BaseModel):
    """What the caller sends."""
    question: str
    k: int = 5


class AskResponse(BaseModel):
    """What we send back."""
    answer: str


def create_app(ask_fn) -> FastAPI:
    """Build the app around an ask function (real one, or a fake in tests)."""
    app = FastAPI(title="AquaRAG")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/ask", response_model=AskResponse)
    def ask_route(req: AskRequest) -> AskResponse:
        # ── Tier 1: your part ──────────────────────────────────────
        # 1. If req.question, stripped, is empty:
        if not req.question.strip():
        #      raise HTTPException(status_code=400, detail="question is empty")
            raise HTTPException(status_code=400, detail="question is empty")
        # 2. Call ask_fn with the question and req.k.
        text = ask_fn(req.question, req.k)
        # 3. Return AskResponse(answer=that text).
        # ───────────────────────────────────────────────────────────
        return AskResponse(answer = text)

    return app


def real_ask(question: str, k: int) -> str:
    """The production ask: open a DB connection and run the pipeline."""
    return ask(connect(), question, k)


app = create_app(real_ask)