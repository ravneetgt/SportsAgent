import feedparser
import re

feeds = {
    "cricket": [
        "https://news.google.com/rss/search?q=international+cricket",
        "https://news.google.com/rss/search?q=cricket+match"
    ],
    "football": [
        "https://news.google.com/rss/search?q=football+soccer",
        "https://news.google.com/rss/search?q=premier+league"
    ],
    "tennis": [
        "https://news.google.com/rss/search?q=tennis+ATP",
        "https://news.google.com/rss/search?q=grand+slam+tennis"
    ],
    "f1": [
        "https://news.google.com/rss/search?q=formula+1",
        "https://news.google.com/rss/search?q=f1+race"
    ]
}


def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def extract_keywords(title):
    words = title.split()
    return " ".join(words[:5])  # simple keyword extraction


def remove_duplicates(articles):
    seen = set()
    unique = []

    for a in articles:
        if a["title"] not in seen:
            unique.append(a)
            seen.add(a["title"])

    return unique


def fetch_news():
    articles = []

    for category, urls in feeds.items():
        print(f"\nFetching {category} news...")

        for url in urls:
            feed = feedparser.parse(url, request_headers={
                'User-Agent': 'Mozilla/5.0'
            })

            for entry in feed.entries[:5]:
                article = {
                    "category": category,
                    "title": entry.title,
                    "summary": clean_html(entry.summary) if "summary" in entry else "",
                    "link": entry.link,
                    "query": extract_keywords(entry.title)
                }

                articles.append(article)

    articles = remove_duplicates(articles)

    print("\nTOTAL ARTICLES:", len(articles))
    return articles


if __name__ == "__main__":
    news = fetch_news()

    for n in news:
        print("\n----------------------")
        print("Category:", n["category"])
        print("Query:", n["query"])
        print("Title:", n["title"])
