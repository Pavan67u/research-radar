import os
os.environ["DATABASE_URL"] = "sqlite://"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Author, Paper, Topic

@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    ml = Topic(name="Machine Learning"); climate = Topic(name="Climate Change")
    ada = Author(name="Ada Lovelace"); grace = Author(name="Grace Hopper")
    for i in range(6):
        p = Paper(openalex_id=f"W{i}", title=f"Paper {i} on models", abstract=f"model science text {i}", publication_year=2024 - i, authors=[ada if i % 2 == 0 else grace], topics=[ml if i < 4 else climate])
        db.add(p)
    db.commit(); db.close()
    def override():
        session = Session()
        try: yield session
        finally: session.close()
    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear(); Base.metadata.drop_all(engine)
