from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Paper

def similar_papers(target: Paper, candidates: list[Paper], limit: int = 5) -> list[Paper]:
    pool = [target] + [paper for paper in candidates if paper.id != target.id]
    if len(pool) < 2:
        return []
    texts = [f"{paper.title} {paper.abstract}" for paper in pool]
    matrix = TfidfVectorizer(stop_words="english").fit_transform(texts)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    ranked = sorted(zip(scores, pool[1:]), key=lambda item: (-item[0], item[1].id))
    return [paper for score, paper in ranked[:limit]]

