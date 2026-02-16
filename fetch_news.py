import feedparser
import re

# Better feeds (more reliable)
feeds = {
    "cricket": "https://news.google.com/rss/search?q=cricket+international&hl=en-IN&gl=IN&ceid=IN:en",
    "football": "https://news.google.com/rss/search?q=football+premier+league&hl=en-GB&gl=GB&ceid=GB:en",
    "tennis": "https://news.google.com/rss/search?q=tennis+ATP+WTA&hl=en-US&gl=US&ceid=US:en",
    "f1": "https://news.google.com/rss/search?q=formula+1+f1&hl=en-GB&gl=GB&ceid=GB:en"
}


# Clean HTML
def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# Remove duplicates
def remove_duplicates(articles):
    seen = set()
    unique = []

    for a in articles:
        if a["title"] not in seen:
            unique.append(a)
            seen.add(a["title"])

    return unique


# Filter good content
def is_interesting(title):
    keywords = [
        # Cricket
        "india", "pakistan", "australia", "england",
        "world cup", "test", "odi", "t20",

        # Football
        "premier league", "champions league",
        "transfer", "goal", "injury",
        "arsenal", "chelsea", "liverpool",
        "real madrid", "barcelona",

        # Tennis
        "grand slam", "wimbledon", "us open",
        "australian open", "roland garros",
        "djokovic", "nadal", "alcaraz", "swiatek",

        # F1
        "f1", "formula 1", "grand prix",
        "verstappen", "hamilton", "ferrari", "red bull"
    ]

    title_lower = title.lower()
    return any(k in title_lower for k in keywords)


# Extract keyword for images
def extract_keyword(title, category):
    title_lower = title.lower()

    entities = [
        # cricket
        "india", "pakistan", "australia", "england",

        # football
        "arsenal", "chelsea", "liverpool",
        "real madrid", "barcelona",

        # tennis
        "djokovic", "nadal", "alcaraz", "swiatek",

        # f1
        "verstappen", "hamilton", "ferrari", "red bull"
    ]

    for e in entities:
        if e in title_lower:
            return e

    return category


# Main function
def fetch_news():
    articles = []

    for category, url in feeds.items():
        print(f"\nFetching {category} news...")

        feed = feedparser.parse(url, request_headers={
            'User-Agent': 'Mozilla/5.0'
        })

        print("Entries found:", len(feed.entries))

        for entry in feed.entries[:10]:
            print("DEBUG TITLE:", entry.title)

            # Filter content (comment this out if nothing returns)
            if not is_interesting(entry.title):
                continue

            article = {
                "category": category,
                "title": entry.title,
                "summary": clean_html(entry.summary) if "summary" in entry else "",
                "link": entry.link,
                "keyword": extract_keyword(entry.title, category)
            }

            articles.append(article)

    articles = remove_duplicates(articles)

    print("\nTOTAL ARTICLES AFTER FILTER:", len(articles))

    return articles


# Test
if __name__ == "__main__":
    news = fetch_news()

    if len(news) == 0:
        print("\n⚠️ No articles returned. Try disabling filter.")
    else:
        for n in news:
            print("\n----------------------")
            print("Category:", n["category"])
            print("Keyword:", n["keyword"])
            print("Title:", n["title"])
            print("Summary:", n["summary"][:150])
