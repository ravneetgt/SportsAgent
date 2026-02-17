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
    words = title.split()
    return " ".join(words[:5])


def fetch_news():
    articles = []

    for category, url in feeds.items():
        print("\nFetching", category)

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:
            articles.append({
                "category": category,
                "title": entry.title,
                "summary": clean_html(entry.summary) if "summary" in entry else "",
                "query": extract_keywords(entry.title)
            })

    return articles
