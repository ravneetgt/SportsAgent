import feedparser
import re
import time
import calendar


# --------------------------------------------------
# RSS SOURCES
# --------------------------------------------------

FEEDS = [
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.theguardian.com/football/rss",
    "https://www.skysports.com/rss/12040",
    "https://www.espn.com/espn/rss/soccer/news",

    # Global football
    "https://www.goal.com/en/rss",
    "https://www.football-italia.net/rss",
]


# --------------------------------------------------
# TOP CLUB DATABASE
# Used to guarantee coverage even if RSS ignores them
# --------------------------------------------------

TOP_CLUBS = {
    "real madrid": "La Liga",
    "barcelona": "La Liga",
    "atletico": "La Liga",

    "bayern": "Bundesliga",
    "dortmund": "Bundesliga",

    "psg": "Ligue 1",

    "inter": "Serie A",
    "milan": "Serie A",
    "juventus": "Serie A",

    "arsenal": "Premier League",
    "chelsea": "Premier League",
    "liverpool": "Premier League",
    "manchester city": "Premier League",
    "manchester united": "Premier League",
    "tottenham": "Premier League"
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
    "conference league"
]


# --------------------------------------------------
# GLOBAL FOOTBALL TERMS
# --------------------------------------------------

GLOBAL_TERMS = [
    "fifa",
    "uefa",
    "transfer",
    "transfer window",
    "contract",
    "loan",
    "bid",
    "signing",
    "medical",
    "release clause",
]


# --------------------------------------------------
# CLEAN HTML
# --------------------------------------------------

def clean_html(text):
    return re.sub("<.*?>", "", text or "")


# --------------------------------------------------
# DETECT CLUB
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

    club, league = detect_club(text)

    if club:
        return True, club, league

    if any(c in text for c in COMPETITIONS):
        return True, None, None

    if any(g in text for g in GLOBAL_TERMS):
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
# CLUB COVERAGE GUARANTEE
# (architectural improvement)
# --------------------------------------------------

def generate_club_watch_items():

    items = []

    for club, league in TOP_CLUBS.items():

        items.append({

            "title": f"{club.title()} watch — latest developments",
            "summary": f"Monitoring news and performance around {club.title()} in {league}.",

            "category": "football",
            "context": "club_watch",

            "teams": [club],
            "league": league,

            "date": int(time.time()),

            "query": f"{club} football match players stadium celebration"
        })

    return items


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

                "query": f"{title} football soccer players stadium crowd"
            })


    # --------------------------------------------------
    # GUARANTEE CLUB COVERAGE
    # --------------------------------------------------

    articles += generate_club_watch_items()


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

    return unique[:100]