"""initial research radar schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table("papers", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("openalex_id", sa.String(255), nullable=False), sa.Column("title", sa.Text(), nullable=False), sa.Column("abstract", sa.Text(), nullable=False), sa.Column("publication_year", sa.Integer()), sa.Column("doi", sa.String(500)), sa.Column("landing_page_url", sa.String(1000)), sa.Column("created_at", sa.DateTime(), nullable=False), sa.UniqueConstraint("openalex_id", name="uq_papers_openalex_id"))
    op.create_index("ix_papers_openalex_id", "papers", ["openalex_id"])
    op.create_index("ix_papers_publication_year", "papers", ["publication_year"])
    op.create_table("authors", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("openalex_id", sa.String(255), unique=True), sa.Column("name", sa.String(500), nullable=False))
    op.create_index("ix_authors_name", "authors", ["name"])
    op.create_table("topics", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(255), nullable=False, unique=True))
    op.create_index("ix_topics_name", "topics", ["name"])
    op.create_table("paper_authors", sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True), sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("paper_topics", sa.Column("paper_id", sa.Integer(), sa.ForeignKey("papers.id", ondelete="CASCADE"), primary_key=True), sa.Column("topic_id", sa.Integer(), sa.ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True))

def downgrade() -> None:
    op.drop_table("paper_topics"); op.drop_table("paper_authors"); op.drop_index("ix_topics_name", table_name="topics"); op.drop_table("topics"); op.drop_index("ix_authors_name", table_name="authors"); op.drop_table("authors"); op.drop_index("ix_papers_publication_year", table_name="papers"); op.drop_index("ix_papers_openalex_id", table_name="papers"); op.drop_table("papers")

