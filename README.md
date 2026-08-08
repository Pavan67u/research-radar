# Research Radar

Research Radar is a focused paper discovery app backed by FastAPI, PostgreSQL, SQLAlchemy/Alembic, Next.js, OpenAlex, and TF-IDF similarity.

## Run

From the repository root:

```bash
docker compose up --build
```

The API is at `http://localhost:8000` and the UI at `http://localhost:3000`. Migrations run automatically when the backend starts. After the services are healthy, ingest 400 records:

```bash
docker compose exec backend python -m scripts.ingest --per-topic 200
```

The API also exposes `/health`, `/papers`, `/papers/{id}`, and `/papers/{id}/similar`.

## Design decisions

Papers, authors, and topics are normalized, with association tables for the two many-to-many relationships. OpenAlex was selected because it provides broad scholarly metadata and an unauthenticated API. Abstracts are reconstructed from its inverted index before storage. TF-IDF with cosine similarity keeps the single AI feature explainable, fast, inexpensive, and runnable without model downloads; it is less semantically rich than embeddings.

## Tradeoffs

The ingestion job targets two fixed broad topics and recent works, with a modest bounded corpus. Search is database `ILIKE`, which is simple and portable but not full-text indexed. Similarity is calculated per request and is appropriate for this assignment-sized dataset; a production corpus would cache vectors. The UI uses straightforward client-side fetches and URL navigation rather than introducing a state library.

## What I'd do next

Add scheduled ingestion with retry/backoff and provenance tracking, PostgreSQL full-text search, cached similarity vectors, richer filter controls, and observability around OpenAlex/API latency.

## Assumptions

“Across 2 topics” is interpreted as two stable seed topics: machine learning and climate change. The default target is 200 works per topic, which yields roughly 400 records while allowing OpenAlex results without an API key. A paper can belong to both topics and is stored once by `openalex_id`.

## Tests

```bash
cd backend
pytest
```

Tests override the database dependency with an in-memory SQLite database and do not require PostgreSQL.

