import re
from datetime import datetime

import feedparser

from app.core.constants import RSS_FEEDS
from app.core.database import SessionLocal
from app.models.news import News


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    cleantext = re.sub(r"http\S+", "", cleantext)
    return " ".join(cleantext.split()).strip()


def parse_and_save_news():
    db = SessionLocal()
    new_items_count = 0

    try:
        for feed_url in RSS_FEEDS:
            parsed_feed = feedparser.parse(feed_url)
            source_name = parsed_feed.feed.get("title", "Источник новостей")

            for entry in parsed_feed.entries[:10]:
                title = entry.get("title")
                link = entry.get("link")

                raw_text = (
                    entry.get("summary")
                    or entry.get("description")
                    or (entry.get("content")[0].value if entry.get("content") else "")
                    or title
                )

                cleaned_text = clean_html(raw_text)

                if len(cleaned_text) < 20:
                    cleaned_text = title

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
                    title=clean_html(title),
                    original_text=cleaned_text,
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
