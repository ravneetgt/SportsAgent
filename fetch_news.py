import feedparser
import re

feeds = {
    "cricket": "https://news.google.com/rss/search?q=international+cricket",
    "football": "https://news.google.com/rss/search?q=football+soccer",
    "tennis": "https://news.google.com/rss/search?q=tennis+ATP",
    "f1": "https://news.google.com/rss/search?q=formula+1"
}


def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def extract_keywords(title):
    # remove noise
    title = title.replace("-", " ").replace(":", " ")

    words = title.split()

    # keep first few meaningful words
    important = [w for w in words if len(w) > 3][:5]

    return " ".join(important)


def build_query(title, category):
    keywords = extract_keywords(title)

    if category == "cricket":
        return f"{keywords} cricket match action"

    if category == "football":
        return f"{keywords} football match stadium action"

    if category == "tennis":
        return f"{keywords} tennis match player action"

    if category == "f1":
        return f"{keywords} formula 1 car race track"

    return f"{keywords} sports"


def fetch_news():
    articles = []

    for category, url in feeds.items():
        print("\nFetching", category)

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            title = entry.title
            summary = clean_html(entry.summary) if "summary" in entry else ""

            query = build_query(title, category)

            articles.append({
                "category": category,
                "title": title,
                "summary": summary,
                "query": query
            })

    return articles
