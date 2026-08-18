from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query

from sqlalchemy.orm import Session

from app.core.constants import MOOD_PROMPTS
from app.core.database import Base, engine, get_db
from app.models.news import News
from app.models.rewritten_news import RewrittenNews
from app.parser import parse_and_save_news
from app.schemas import NewsResponse, RewrittenNewsResponse
from app.services.ai_service import rewrite_news_with_ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = SessionLocal = next(get_db())
    if db.query(News).count() == 0:
        parse_and_save_news()

    yield


app = FastAPI(title="News Mood App", lifespan=lifespan)


@app.get("/api/news", response_model=List[NewsResponse])
def get_news(skip: int = 0, limit: int = 15, db: Session = Depends(get_db)):
    news_items = db.query(News).order_by(News.published_at.desc()).offset(skip).limit(limit).all()
    return news_items


@app.post("/api/news/{news_id}/rewrite", response_model=RewrittenNewsResponse)
def get_rewritten_news(
        news_id: int,
        mood: str = Query(
            ...,
            description="Настроение: joy, sad, irony, neutral",
        ),
        force_update: bool = Query(
            False,
            description="Принудительно перегенерировать через ИИ",
        ),
        db: Session = Depends(get_db),
):
    if mood not in MOOD_PROMPTS:
        raise HTTPException(
            status_code=400,
            detail="Неверное настроение. Доступные: joy, sad, irony, neutral",
        )

    news_item = db.query(News).filter(News.id == news_id).first()
    if not news_item:
        raise HTTPException(
            status_code=404,
            detail="Новость не найдена",
        )

    cached_rewrite = (
        db.query(RewrittenNews)
        .filter(
            RewrittenNews.news_id == news_id,
            RewrittenNews.mood == mood,
        )
        .first()
    )

    if cached_rewrite and not force_update:
        return cached_rewrite

    new_text = rewrite_news_with_ai(news_item.original_text, mood)

    if cached_rewrite:
        cached_rewrite.rewritten_text = new_text
        db.commit()
        db.refresh(cached_rewrite)
        result = cached_rewrite
    else:
        new_rewrite = RewrittenNews(news_id=news_id, mood=mood, rewritten_text=new_text)
        db.add(new_rewrite)
        db.commit()
        db.refresh(new_rewrite)
        result = new_rewrite

    return result


@app.post("/api/news/refresh")
def refresh_news():
    try:
        parse_and_save_news()
        return {
            "status": "success",
            "message": "Новости успешно обновлены",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
