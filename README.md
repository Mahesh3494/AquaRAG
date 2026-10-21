# AquaRAG

![tests](https://github.com/Mahesh3494/AquaRAG/actions/workflows/tests.yml/badge.svg)

AquaRAG is a chatbot that answers shrimp and fish farmers' questions about
aquaculture, using four published aquaculture manuals as its knowledge source.
Every answer cites the document and page it came from, and when the answer
isn't in the manuals it says so instead of guessing. It will be the chatbot
inside AquaManage, my aquaculture farm platform, alongside AquaVision.

## How it works

1. **Indexing:** the PDFs are split into overlapping chunks of about 1000
   characters, and each chunk keeps its source document and page number.
2. **Search:** a question is matched against all chunks with BM25 keyword
   search, which keeps the top 20 candidates.
3. **Rerank:** a cross-encoder (`ms-marco-MiniLM-L-6-v2`) reads the question
   and each candidate together, re-scores them, and keeps the best 5.
4. **Answer:** those 5 chunks go to the LLM (DeepSeek) with instructions to
   answer only from them and to cite each claim as `[n]`. If they don't
   contain the answer, it replies "Not found in the provided documents."

There is also an **agent mode**, where the LLM decides for itself when to search
and what to search for. On the evaluation it scored about the same as the
pipeline (43/49 vs 44/49) but takes two LLM calls per question instead of one,
so the simpler pipeline is the default.

## Results

Measured on a golden dataset of 49 questions, each labelled with the document
and page that contains its answer: 20 written by hand, plus 29 LLM-generated
questions, each manually verified against the source PDF.

**Retrieval:** a "hit" means the correct page appears in the top *k* chunks.

| Method | hit@1 | hit@5 |
|---|---|---|
| Dense (MiniLM embeddings, pgvector) | 60% | 74% |
| Keyword (BM25) | 72% | 94% |
| Hybrid (BM25 + dense, RRF) | 70% | 94% |
| **BM25 + cross-encoder rerank** | **84%** | **98%** |

**Answers:** each answer was graded CORRECT/INCORRECT by an LLM judge against
the reference answer, at temperature 0.

| Mode | Correct |
|---|---|
| **Pipeline (default)** | **44 / 49** |
| Agent | 43 / 49 |

## What didn't work

- **Dense embeddings alone** were the weakest retriever. Aquaculture questions
  depend on exact terms (species names, chemicals, units), which BM25 matches
  directly.
- **Hybrid search (RRF)** gave no gain over BM25 alone.
- **Page-level fusion** made results worse, because pages with many chunks
  collected more points.
- **Agent mode** didn't beat the simpler pipeline.
- **Caveat:** with 49 questions, one question is about 2 percentage points, so
  differences of one or two questions are within noise.

## Run it yourself

Requires Docker.

```bash
git clone https://github.com/Mahesh3494/AquaRAG.git
cd AquaRAG
cp .env.example .env          # then put your DeepSeek key and a DB password in .env
```

Download the PDFs listed in [corpus/SOURCES.md](corpus/SOURCES.md) into `corpus/`
(they are not included in this repo for licensing reasons).

```bash
docker compose up -d --build
docker compose run --rm api python -m scripts.index_corpus
```

Open http://localhost:8000/docs and try `POST /ask`.

## Tests

```bash
pytest
```

Run tests from your local venv, **not** inside the compose container. The tests
drop and recreate the `chunks` table in whatever database `DATABASE_URL` points to.

## Built with

Python · PostgreSQL + pgvector · rank-bm25 · sentence-transformers · FastAPI · Docker · DeepSeek API