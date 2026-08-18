from app.core.database import Base

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


class RewrittenNews(Base):
    __tablename__ = "rewritten_news"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    news_id = Column(
        Integer,
        ForeignKey(
            "news.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    mood = Column(
        String(50),
        nullable=False,
    )
    rewritten_text = Column(
        Text,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "news_id",
            "mood",
            name="uq_news_mood",
        ),
    )

    news = relationship(
        "News",
        back_populates="rewrites",
    )
