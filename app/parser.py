from datetime import datetime

import feedparser

from app.core.database import SessionLocal
from app.core.constants import RSS_FEEDS
from app.models.news import News


def parse_and_save_news():
    db = SessionLocal()
    new_items_count = 0

    try:
        for feed_url in RSS_FEEDS:
            parsed_feed = feedparser.parse(feed_url)
            source_name = parsed_feed.feed.get("title", "Unknown Source")

            for entry in parsed_feed.entries[:10]:
                title = entry.get("title")
                link = entry.get("link")
                summary = entry.get("summary", title)

                existing_news = db.query(News).filter(News.source_url == link).first()
                if existing_news:
                    continue

                published_at = datetime.now()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                db_news = News(
                    title=title,
                    original_text=summary,
                    source_url=link,
                    source_name=source_name,
                    published_at=published_at,
                )

                db.add(db_news)
                new_items_count += 1

        db.commit()

    except Exception as e:
        db.rollback()
    finally:
        db.close()
