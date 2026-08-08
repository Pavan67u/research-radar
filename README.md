# Research Radar

Research Radar is a focused paper discovery app backed by FastAPI, PostgreSQL, SQLAlchemy/Alembic, Next.js, OpenAlex, and TF-IDF similarity.

## Run

From the repository root:

```bash
docker compose up --build
```

The API is at `http://localhost:8000` and the UI at `http://localhost:3000`. Migrations run automatically when the backend starts. After the services are healthy, ingest 400 records:

```bash
docker compose exec backend python -m scripts.ingest --per-topic 100
```

The API also exposes `/health`, `/papers`, `/papers/{id}`, and `/papers/{id}/similar`.

## Design decisions

Papers, authors, and topics are normalized, with association tables for the two many-to-many relationships. OpenAlex was selected because it provides broad scholarly metadata and an unauthenticated API. Abstracts are reconstructed from its inverted index before storage. TF-IDF with cosine similarity keeps the single AI feature explainable, fast, inexpensive, and runnable without model downloads; it is less semantically rich than embeddings.

## Tradeoffs

The ingestion job targets five distinct OpenAlex topics and 100 recent works per topic. Search is database `ILIKE`, which is simple and portable but not full-text indexed. Similarity is calculated per request and is appropriate for this assignment-sized dataset; a production corpus would cache vectors. The UI uses straightforward client-side fetches and URL navigation rather than introducing a state library.

## What I'd do next

Add scheduled ingestion with retry/backoff and provenance tracking, PostgreSQL full-text search, cached similarity vectors, richer filter controls, and observability around OpenAlex/API latency.

## Assumptions

The initial assignment requested two topics; the current configuration expands this to five stable OpenAlex topics with a default target of 100 works each: materials-focused machine learning, climate change, neural network applications, cancer research, and renewable energy. A paper can belong to multiple topics and is stored once by `openalex_id`.

## Tests

```bash
cd backend
pytest
```

Tests override the database dependency with an in-memory SQLite database and do not require PostgreSQL.
