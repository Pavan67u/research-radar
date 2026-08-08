from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

paper_authors = Table(
    "paper_authors", Base.metadata,
    Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("author_id", ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True),
)
paper_topics = Table(
    "paper_topics", Base.metadata,
    Column("paper_id", ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
)


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (UniqueConstraint("openalex_id", name="uq_papers_openalex_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    openalex_id: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(Text)
    abstract: Mapped[str] = mapped_column(Text, default="")
    publication_year: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    doi: Mapped[str | None] = mapped_column(String(500), nullable=True)
    landing_page_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    authors: Mapped[list["Author"]] = relationship(secondary=paper_authors, back_populates="papers")
    topics: Mapped[list["Topic"]] = relationship(secondary=paper_topics, back_populates="papers")


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    openalex_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(500), index=True)
    papers: Mapped[list[Paper]] = relationship(secondary=paper_authors, back_populates="authors")


class Topic(Base):
    __tablename__ = "topics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    papers: Mapped[list[Paper]] = relationship(secondary=paper_topics, back_populates="topics")

