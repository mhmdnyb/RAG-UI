"""Database schema for regulation articles."""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RegulationArticle(Base):
    """Parent regulation article entity."""

    __tablename__ = "regulation_articles"

    id = Column(String, primary_key=True)
    section = Column(String)
    title = Column(String)
    full_text = Column(Text, nullable=False)
