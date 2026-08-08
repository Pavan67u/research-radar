from math import ceil
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from .config import settings
from .database import get_db
from .models import Author, Paper, Topic
from .schemas import PaperDetail, PaperPage, PaperSummary
from .similarity import similar_papers

app = FastAPI(title="Research Radar API")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def paper_query():
    return select(Paper).options(selectinload(Paper.authors), selectinload(Paper.topics))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/topics", response_model=list[str])
def list_topics(db: Session = Depends(get_db)):
    return db.scalars(select(Topic.name).distinct().order_by(Topic.name)).all()

@app.get("/years", response_model=list[int])
def list_years(db: Session = Depends(get_db)):
    return db.scalars(select(Paper.publication_year).where(Paper.publication_year.is_not(None)).distinct().order_by(Paper.publication_year.desc())).all()

@app.get("/papers", response_model=PaperPage)
def list_papers(db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), q: str | None = None, year: int | None = None, topic: str | None = None, author: str | None = None):
    stmt = paper_query()
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Paper.title.ilike(term), Paper.abstract.ilike(term)))
    if year is not None:
        stmt = stmt.where(Paper.publication_year == year)
    if topic:
        stmt = stmt.join(Paper.topics).where(Topic.name.ilike(f"%{topic.strip()}%"))
    if author:
        stmt = stmt.join(Paper.authors).where(Author.name.ilike(f"%{author.strip()}%"))
    count_stmt = stmt.with_only_columns(func.count(Paper.id)).order_by(None).distinct()
    total = db.scalar(count_stmt) or 0
    items = db.scalars(stmt.order_by(Paper.publication_year.desc().nullslast(), Paper.id.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return PaperPage(items=items, page=page, page_size=page_size, total=total, pages=ceil(total / page_size) if total else 0)

@app.get("/papers/{paper_id}", response_model=PaperDetail)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.scalar(paper_query().where(Paper.id == paper_id))
    if not paper:
        raise HTTPException(404, "Paper not found")
    return paper

@app.get("/papers/{paper_id}/similar", response_model=list[PaperSummary])
def get_similar(paper_id: int, db: Session = Depends(get_db)):
    target = db.scalar(paper_query().where(Paper.id == paper_id))
    if not target:
        raise HTTPException(404, "Paper not found")
    candidates = db.scalars(paper_query()).unique().all()
    return similar_papers(target, candidates)
