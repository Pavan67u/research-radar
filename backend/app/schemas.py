from pydantic import BaseModel, ConfigDict

class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str

class PaperSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    abstract: str
    publication_year: int | None
    authors: list[AuthorOut]
    topics: list[TopicOut]

class PaperDetail(PaperSummary):
    openalex_id: str
    doi: str | None
    landing_page_url: str | None

class PaperPage(BaseModel):
    items: list[PaperSummary]
    page: int
    page_size: int
    total: int
    pages: int

