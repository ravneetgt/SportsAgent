import feedparser
import re


# -----------------------------
# FEEDS (MULTI-SOURCE)
# -----------------------------
feeds = {
    # -----------------------------
    # CRICKET
    # -----------------------------
    "cricket": "https://news.google.com/rss/search?q=international+cricket",
    "cricket_cricinfo": "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "cricket_wisden": "https://www.wisden.com/feed",

    # -----------------------------
    # FOOTBALL
    # -----------------------------
    "football": "https://news.google.com/rss/search?q=football+soccer",
    "football_guardian": "https://www.theguardian.com/football/rss",
    "football_bbc": "http://feeds.bbci.co.uk/sport/football/rss.xml",

    # -----------------------------
    # TENNIS
    # -----------------------------
    "tennis": "https://news.google.com/rss/search?q=tennis+ATP",
    "tennis_atp": "https://www.atptour.com/en/media/rss-feed/xml-feed",

    # -----------------------------
    # F1
    # -----------------------------
    "f1": "https://news.google.com/rss/search?q=formula+1",
    "f1_official": "https://www.formula1.com/en/latest/all.xml",
    "f1_race": "https://the-race.com/category/formula-1/feed/",
}


# -----------------------------
# CLEAN HTML
# -----------------------------
def clean_html(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


# -----------------------------
# NORMALIZE CATEGORY
# -----------------------------
def normalize_category(category):
    c = category.lower()

    if "cricket" in c:
        return "cricket"
    if "football" in c:
        return "football"
    if "tennis" in c:
        return "tennis"
    if "f1" in c or "formula" in c:
        return "f1"

    return "other"


# -----------------------------
# KEYWORD EXTRACTION (IMPROVED)
# -----------------------------
def extract_keywords(title):
    title = title.lower()

    # remove punctuation
    title = re.sub(r'[^\w\s]', '', title)

    words = title.split()

    # remove common filler words
    stopwords = {
        "the", "and", "with", "from", "this", "that",
        "after", "before", "over", "into", "for",
        "vs", "live", "report", "highlights"
    }

    keywords = [w for w in words if w not in stopwords and len(w) > 3]

    return " ".join(keywords[:6])


# -----------------------------
# BUILD IMAGE QUERY (SMARTER)
# -----------------------------
def build_query(title, category):
    keywords = extract_keywords(title)

    if category == "cricket":
        return f"{keywords} cricket action match stadium player"

    if category == "football":
        return f"{keywords} football soccer match stadium player action"

    if category == "tennis":
        return f"{keywords} tennis player action court match"

    if category == "f1":
        return f"{keywords} formula 1 car racing track action"

    return f"{keywords} sports action"


# -----------------------------
# REMOVE DUPLICATES
# -----------------------------
def remove_duplicates(articles):
    seen = set()
    unique = []

    for a in articles:
        key = a["title"].strip().lower()

        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique


# -----------------------------
# FETCH NEWS
# -----------------------------
def fetch_news():
    articles = []

    for raw_category, url in feeds.items():
        print("\nFetching", raw_category)

        try:
            feed = feedparser.parse(url)

            print("Entries:", len(feed.entries))

            for entry in feed.entries[:5]:
                title = entry.title.strip()

                summary = ""
                if hasattr(entry, "summary"):
                    summary = clean_html(entry.summary)

                category = normalize_category(raw_category)

                query = build_query(title, category)

                articles.append({
                    "category": category,
                    "title": title,
                    "summary": summary,
                    "query": query
                })

        except Exception as e:
            print("Feed error:", raw_category, e)

    articles = remove_duplicates(articles)

    print("\nTOTAL UNIQUE ARTICLES:", len(articles))

    return articles
