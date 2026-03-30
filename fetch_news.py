import feedparser
import re
import time
import calendar


FEEDS = [
    # ── UK / Premier League ──────────────────────────────
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.theguardian.com/football/rss",
    "https://www.skysports.com/rss/12040",
    "https://www.goal.com/en/rss",
    "https://www.90min.com/feeds/latest.rss",

    # ── Champions League / UEFA ──────────────────────────
    "https://www.uefa.com/uefachampionsleague/rss/news/",
    "https://www.uefa.com/uefaeuropaleague/rss/news/",

    # ── La Liga / Spain ──────────────────────────────────
    "https://www.marca.com/en/football/rss2.xml",
    "https://managingmadrid.com/rss/current.xml",
    "https://www.barcablaugranes.com/rss/current.xml",

    # ── Bundesliga / Germany ─────────────────────────────
    "https://bavarian-football-works.com/rss/current.xml",
    "https://bulinews.com/feed/",

    # ── Serie A / Italy ──────────────────────────────────
    "https://www.football-italia.net/feed",
    "https://sempreinter.com/feed",

    # ── Ligue 1 / France ─────────────────────────────────
    "https://parisbeaumonde.com/feed",
    "https://thebusbybabe.sbnation.com/rss/current.xml",

    # ── FIFA / International ─────────────────────────────
    "https://www.fourfourtwo.com/news/rss",
    "https://www.espn.com/espn/rss/soccer/news",

    # ── Transfers ────────────────────────────────────────
    "https://www.givemesport.com/rss/football",
]


TOP_CLUBS = {

    # Spain
    "real madrid": "La Liga",
    "madrid": "La Liga",
    "barcelona": "La Liga",
    "barca": "La Liga",
    "atletico": "La Liga",

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

    # Germany
    "bayern": "Bundesliga",
    "bayern munich": "Bundesliga",
    "dortmund": "Bundesliga",
    "rb leipzig": "Bundesliga",

    # Italy
    "inter": "Serie A",
    "inter milan": "Serie A",
    "ac milan": "Serie A",
    "milan": "Serie A",
    "juventus": "Serie A",
    "napoli": "Serie A",
    "roma": "Serie A",

    # France
    "psg": "Ligue 1",
    "paris saint germain": "Ligue 1",
    "marseille": "Ligue 1",
    "lyon": "Ligue 1"
}


COMPETITIONS = [
    "premier league",
    "la liga",
    "serie a",
    "bundesliga",
    "champions league",
    "europa league",
    "conference league"
]


GLOBAL_TERMS = [
    "fifa",
    "uefa",
    "transfer",
    "contract",
    "loan",
    "bid",
    "signing",
    "medical",
]


def clean_html(text):
    return re.sub("<.*?>", "", text or "")


def detect_club(text):

    text = text.lower()

    for club, league in TOP_CLUBS.items():
        if club in text:
            return club.title(), league

    return None, None


def is_relevant(title, summary):

    text = f"{title} {summary}".lower()

    banned = ["nfl", "super bowl", "touchdown"]
    if any(b in text for b in banned):
        return False, None, None

    club, league = detect_club(text)

    if club:
        return True, club, league

    if any(c in text for c in COMPETITIONS):

        if "bundesliga" in text:
            return True, None, "Bundesliga"

        if "serie a" in text:
            return True, None, "Serie A"

        if "ligue 1" in text:
            return True, None, "Ligue 1"

        return True, None, None

    if any(g in text for g in GLOBAL_TERMS):
        return True, None, None

    return False, None, None


def parse_timestamp(entry):

    t = entry.get("published_parsed")

    if t:
        try:
            return int(calendar.timegm(t))
        except:
            pass

    return int(time.time())


def generate_club_watch_items():

    items = []

    for club, league in TOP_CLUBS.items():

        items.append({
            "title": f"{club.title()} watch — latest developments",
            "summary": f"Monitoring {club.title()} in {league}.",
            "category": "football",
            "context": "club_watch",
            "teams": [club],
            "league": league,
            "date": int(time.time()),
            "query": f"{club} football match stadium players"
        })

    return items


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
                "query": f"{title} football match players stadium"
            })

    articles += generate_club_watch_items()

    seen = set()
    unique = []

    for a in articles:
        key = a["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique[:100]