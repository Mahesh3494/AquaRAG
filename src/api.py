"""HTTP API for AquaRAG."""
import psycopg
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.pipeline import EmptyIndexError, ask
from src.store import connect


class AskRequest(BaseModel):
    """What the caller sends."""
    question: str
    # 1 to 20: rerank only ever sees CANDIDATES (20) chunks, and 0 would
    # leave build_prompt with nothing to work from.
    k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    """One chunk the answer could cite. [n] in the answer means this one."""
    n: int
    source_doc: str
    page: int


class AskResponse(BaseModel):
    """What we send back."""
    answer: str
    sources: list[Source]


def create_app(ask_fn) -> FastAPI:
    """Build the app around an ask function (real one, or a fake in tests).

    ask_fn(question, k) returns (answer text, results), like pipeline.ask.
    """
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
        # Each failure below is something AquaRAG depends on being down, not a
        # bug in the request, so it's 503 (try again later), never a bare 500.
        try:
            text, results = ask_fn(req.question, req.k)
        except EmptyIndexError:
            raise HTTPException(
                status_code=503,
                detail="nothing is indexed yet: run python -m scripts.index_corpus",
            )
        except requests.RequestException:
            # Timeout, no network, or DeepSeek answered with an error (bad key, no credit).
            raise HTTPException(status_code=503, detail="the language model did not answer")
        except psycopg.OperationalError:
            raise HTTPException(status_code=503, detail="the database is not reachable")
        # 3. Return the answer, plus what each [n] points at (n counts from 1,
        #    the same numbering build_prompt gave the model).
        # ───────────────────────────────────────────────────────────
        sources = []
        for n, result in enumerate(results, start=1):
            sources.append(Source(n=n, source_doc=result["source_doc"], page=result["page"]))
        return AskResponse(answer=text, sources=sources)

    return app


def real_ask(question: str, k: int) -> tuple[str, list[dict]]:
    """The production ask: open a DB connection, run the pipeline, close it.

    `with` closes the connection even if ask() raises. Without it, every
    question left one connection open until Postgres ran out (~100).
    """
    with connect() as conn:
        return ask(conn, question, k)


app = create_app(real_ask)
