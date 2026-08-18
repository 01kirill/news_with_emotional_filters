from app.core.database import Base

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class News(Base):
    __tablename__ = "news"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    title = Column(
        String(255),
        nullable=False,
    )
    original_text = Column(
        Text,
        nullable=False,
    )
    source_url = Column(
        String(512),
        unique=True,
        nullable=False,
    )
    source_name = Column(
        String(100),
        nullable=False,
    )
    published_at = Column(
        DateTime,
        nullable=False,
    )

    rewrites = relationship(
        "RewrittenNews",
        back_populates="news",
        cascade="all, delete-orphan",
    )
