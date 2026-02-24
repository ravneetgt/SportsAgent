import feedparser
import re

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


def fetch_news():
    articles = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = clean_html(entry.get("summary", ""))

            if not title or not is_relevant(title):
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "category": "football",
                "context": "news"
            })

    # dedupe
    seen = set()
    unique = []

    for a in articles:
        key = a["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique[:20]