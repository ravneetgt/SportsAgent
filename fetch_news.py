import feedparser
import re
import time
import calendar

FEEDS = [
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.theguardian.com/football/rss",
    "https://www.skysports.com/rss/12040",
    "https://www.espn.com/espn/rss/soccer/news",
]

KEYWORDS = [
    "premier league", "la liga", "serie a", "bundesliga",
    "champions league", "europa league",
    "manchester", "arsenal", "chelsea", "liverpool",
    "real madrid", "barcelona", "bayern", "psg", "inter", "milan"
]


def clean_html(text):
    return re.sub('<.*?>', '', text or "")


def is_relevant(title):
    t = title.lower()

    banned = ["nfl", "super bowl", "touchdown"]
    if any(b in t for b in banned):
        return False

    return any(k in t for k in KEYWORDS)


def parse_timestamp(entry):
    """Extract Unix timestamp from feedparser entry. Falls back to now."""
    t = entry.get("published_parsed")
    if t:
        try:
            return int(calendar.timegm(t))
        except Exception:
            pass
    return int(time.time())


def fetch_news():
    articles = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title   = entry.get("title", "")
            summary = clean_html(entry.get("summary", ""))

            if not title or not is_relevant(title):
                continue

            articles.append({
                "title":    title,
                "summary":  summary,
                "category": "football",
                "context":  "news",
                "date":     parse_timestamp(entry),   # ← feeds rank_news recency boost
                "query":    f"{title} football soccer player action stadium"
            })

    # dedupe by title
    seen   = set()
    unique = []

    for a in articles:
        key = a["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique[:20]
