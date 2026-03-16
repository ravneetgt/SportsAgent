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


# --------------------------------------------------
# TOP CLUB DATABASE
# --------------------------------------------------

TOP_CLUBS = {
    # England
    "arsenal": "Premier League",
    "chelsea": "Premier League",
    "liverpool": "Premier League",
    "manchester city": "Premier League",
    "man city": "Premier League",
    "manchester united": "Premier League",
    "man united": "Premier League",
    "tottenham": "Premier League",
    "spurs": "Premier League",
    "newcastle": "Premier League",

    # Spain
    "real madrid": "La Liga",
    "madrid": "La Liga",
    "barcelona": "La Liga",
    "barca": "La Liga",
    "atletico": "La Liga",

    # Germany
    "bayern": "Bundesliga",
    "dortmund": "Bundesliga",

    # France
    "psg": "Ligue 1",
    "paris saint-germain": "Ligue 1",

    # Italy
    "inter": "Serie A",
    "milan": "Serie A",
    "juventus": "Serie A"
}


# --------------------------------------------------
# COMPETITIONS
# --------------------------------------------------

COMPETITIONS = [
    "premier league",
    "la liga",
    "serie a",
    "bundesliga",
    "champions league",
    "europa league",
    "conference league",
    "world cup",
    "euros"
]


# --------------------------------------------------
# GLOBAL FOOTBALL SIGNALS
# --------------------------------------------------

GLOBAL_TERMS = [
    "fifa",
    "uefa",
    "transfer",
    "transfer window",
    "signing",
    "contract",
    "loan deal",
    "bid rejected",
    "medical",
    "interest in",
    "release clause",
    "international break",
    "national team"
]


# --------------------------------------------------
# CLEAN HTML
# --------------------------------------------------

def clean_html(text):
    return re.sub('<.*?>', '', text or "")


# --------------------------------------------------
# CLUB DETECTION
# --------------------------------------------------

def detect_club(text):

    text = text.lower()

    for club, league in TOP_CLUBS.items():
        if club in text:
            return club, league

    return None, None


# --------------------------------------------------
# RELEVANCE CHECK
# --------------------------------------------------

def is_relevant(title, summary):

    text = f"{title} {summary}".lower()

    banned = ["nfl", "super bowl", "touchdown"]
    if any(b in text for b in banned):
        return False, None, None

    # club signal
    club, league = detect_club(text)
    if club:
        return True, club, league

    # competition signal
    if any(c in text for c in COMPETITIONS):
        return True, None, None

    # transfer / governance signal
    if any(k in text for k in GLOBAL_TERMS):
        return True, None, None

    return False, None, None


# --------------------------------------------------
# TIMESTAMP
# --------------------------------------------------

def parse_timestamp(entry):

    t = entry.get("published_parsed")

    if t:
        try:
            return int(calendar.timegm(t))
        except:
            pass

    return int(time.time())


# --------------------------------------------------
# FETCH NEWS
# --------------------------------------------------

def fetch_news():

    articles = []

    for url in FEEDS:

        feed = feedparser.parse(url)

        for entry in feed.entries:

            title = entry.get("title", "")
            summary = clean_html(entry.get("summary", ""))

            if not title:
                continue

            relevant, club, league = is_relevant(title, summary)

            if not relevant:
                continue

            articles.append({

                "title": title,
                "summary": summary,

                "category": "football",
                "context": "news",

                "teams": [club] if club else [],
                "league": league if league else "",

                "date": parse_timestamp(entry),

                "query": f"{title} football soccer players stadium crowd match"
            })


    # --------------------------------------------------
    # DEDUPE
    # --------------------------------------------------

    seen = set()
    unique = []

    for a in articles:

        key = a["title"].lower()

        if key not in seen:
            seen.add(key)
            unique.append(a)

    # return more stories so nothing important is lost
    return unique[:60]