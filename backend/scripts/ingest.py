"""Fetch a small, repeatable OpenAlex corpus for two research areas."""
import argparse
import time
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Author, Paper, Topic

API = "https://api.openalex.org/works"
TOPICS = {"machine learning": "T10757", "climate change": "T18427"}

def reconstruct_abstract(index: dict | None) -> str:
    if not index:
        return ""
    words = [(position, word) for word, positions in index.items() for position in positions]
    return " ".join(word for _, word in sorted(words))

def get_or_create(db: Session, model, lookup: dict, values: dict | None = None):
    item = db.scalar(select(model).filter_by(**lookup))
    if item:
        return item
    item = model(**lookup, **(values or {}))
    db.add(item)
    db.flush()
    return item

def ingest_topic(db: Session, client: httpx.Client, label: str, topic_id: str, per_topic: int) -> int:
    cursor = "*"
    saved = 0
    while cursor and saved < per_topic:
        response = client.get(API, params={"filter": f"topics.id:{topic_id},from_publication_date:2020-01-01", "sort": "publication_date:desc", "per-page": min(200, per_topic - saved), "cursor": cursor})
        response.raise_for_status()
        payload = response.json()
        for raw in payload.get("results", []):
            openalex_id = raw.get("id")
            if not openalex_id:
                continue
            paper = db.scalar(select(Paper).where(Paper.openalex_id == openalex_id))
            if not paper:
                paper = Paper(openalex_id=openalex_id, title=raw.get("title") or "Untitled", abstract=reconstruct_abstract(raw.get("abstract_inverted_index")), publication_year=raw.get("publication_year"), doi=raw.get("doi"), landing_page_url=raw.get("primary_location", {}).get("landing_page_url"))
                db.add(paper)
                db.flush()
            else:
                paper.title = raw.get("title") or paper.title
                paper.abstract = reconstruct_abstract(raw.get("abstract_inverted_index")) or paper.abstract
                paper.publication_year = raw.get("publication_year") or paper.publication_year
            topic = get_or_create(db, Topic, {"name": label})
            if topic not in paper.topics:
                paper.topics.append(topic)
            authors = []
            for authorship in raw.get("authorships", []):
                author_raw = authorship.get("author") or {}
                name = author_raw.get("display_name")
                if not name:
                    continue
                author = get_or_create(db, Author, {"openalex_id": author_raw.get("id")}, {"name": name}) if author_raw.get("id") else get_or_create(db, Author, {"name": name})
                authors.append(author)
            paper.authors = authors
            saved += 1
        cursor = payload.get("meta", {}).get("next_cursor")
        if not payload.get("results"):
            break
    return saved

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-topic", type=int, default=200)
    args = parser.parse_args()
    with httpx.Client(timeout=30, headers={"User-Agent": "research-radar/1.0"}) as client, SessionLocal() as db:
        total = sum(ingest_topic(db, client, label, topic_id, args.per_topic) for label, topic_id in TOPICS.items())
        db.commit()
    print(f"Ingested {total} records across {len(TOPICS)} topics")

if __name__ == "__main__":
    main()

