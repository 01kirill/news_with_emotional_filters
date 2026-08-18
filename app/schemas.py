from datetime import datetime
from typing import List

from pydantic import BaseModel


class RewrittenNewsResponse(BaseModel):
    mood: str
    rewritten_text: str

    class Config:
        from_attributes = True


class NewsResponse(BaseModel):
    id: int
    title: str
    original_text: str
    source_url: str
    source_name: str
    published_at: datetime
    rewrites: List[RewrittenNewsResponse] = []

    class Config:
        from_attributes = True


class RewriteRequest(BaseModel):
    mood: str
    force_update: bool = False
