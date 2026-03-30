import feedparser
import re
import time
import calendar


# --------------------------------------------------
# RSS SOURCES
# --------------------------------------------------

FEEDS = [
    # ── Premier League ────────────────────────────────────
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://www.theguardian.com/football/rss",
    "https://www.skysports.com/rss/12040",
    "https://www.goal.com/en/rss",
    "https://www.90min.com/feeds/latest.rss",
    "https://www.givemesport.com/rss/football",

    # ── Champions League / UEFA ───────────────────────────
    "https://www.espn.com/espn/rss/soccer/news",
    "https://www.fourfourtwo.com/news/rss",

    # ── La Liga / Spain ───────────────────────────────────
    "https://www.marca.com/en/football/rss2.xml",
    "https://managingmadrid.com/rss/current.xml",
    "https://www.barcablaugranes.com/rss/current.xml",

    # ── Bundesliga / Germany ──────────────────────────────
    "https://bavarian-football-works.com/rss/current.xml",
    "https://bulinews.com/feed/",

    # ── Serie A / Italy ───────────────────────────────────
    "https://www.football-italia.net/feed",
    "https://sempreinter.com/feed",

    # ── Ligue 1 / France ─────────────────────────────────
    "https://parisbeaumonde.com/feed",

    # ── FIFA / International ──────────────────────────────
    "https://www.fifaindex.com/news/feed/",
]


# --------------------------------------------------
# CLUB → LEAGUE MAP
# --------------------------------------------------

TOP_CLUBS = {
    # Spain
    "real madrid":          "La Liga",
    "madrid":               "La Liga",
    "barcelona":            "La Liga",
    "barca":                "La Liga",
    "atletico":             "La Liga",
    "atletico madrid":      "La Liga",
    "sevilla":              "La Liga",
    "villarreal":           "La Liga",

    # England
    "arsenal":              "Premier League",
    "chelsea":              "Premier League",
    "liverpool":            "Premier League",
    "manchester city":      "Premier League",
    "man city":             "Premier League",
    "manchester united":    "Premier League",
    "man united":           "Premier League",
    "tottenham":            "Premier League",
    "spurs":                "Premier League",
    "newcastle":            "Premier League",
    "aston villa":          "Premier League",
    "brighton":             "Premier League",
    "west ham":             "Premier League",

    # Germany
    "bayern":               "Bundesliga",
    "bayern munich":        "Bundesliga",
    "dortmund":             "Bundesliga",
    "borussia dortmund":    "Bundesliga",
    "rb leipzig":           "Bundesliga",
    "leverkusen":           "Bundesliga",
    "bayer leverkusen":     "Bundesliga",

    # Italy
    "inter":                "Serie A",
    "inter milan":          "Serie A",
    "ac milan":             "Serie A",
    "milan":                "Serie A",
    "juventus":             "Serie A",
    "napoli":               "Serie A",
    "roma":                 "Serie A",
    "lazio":                "Serie A",
    "atalanta":             "Serie A",

    # France
    "psg":                  "Ligue 1",
    "paris saint-germain":  "Ligue 1",
    "paris saint germain":  "Ligue 1",
    "marseille":            "Ligue 1",
    "lyon":                 "Ligue 1",
    "monaco":               "Ligue 1",
    "lille":                "Ligue 1",
    "nice":                 "Ligue 1",

    # International / FIFA
    "england":              "International",
    "france":               "International",
    "germany":              "International",
    "spain":                "International",
    "brazil":               "International",
    "argentina":            "International",
    "portugal":             "International",
    "italy":                "International",
    "netherlands":          "International",
    "belgium":              "International",
}


# --------------------------------------------------
# COMPETITIONS TO DETECT
# --------------------------------------------------

COMPETITIONS = [
    "premier league",
    "la liga",
    "serie a",
    "bundesliga",
    "ligue 1",
    "champions league",
    "europa league",
    "conference league",
    "world cup",
    "euros",
    "euro 2024",
    "nations league",
    "copa del rey",
    "fa cup",
    "carabao cup",
    "dfb pokal",
    "coppa italia",
    "coupe de france",
    "ballon d'or",
    "golden boot",
]


# --------------------------------------------------
# GLOBAL FOOTBALL TERMS
# --------------------------------------------------

GLOBAL_TERMS = [
    "fifa",
    "uefa",
    "transfer",
    "contract",
    "loan",
    "bid",
    "signing",
    "medical",
    "world cup",
    "international",
    "national team",
    "qualifier",
    "euros",
    "nations league",
    "ballon d'or",
    "golden boot",
    "manager sacked",
    "new manager",
    "record fee",
    "release clause",
]


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def clean_html(text):
    return re.sub("<.*?>", "", text or "")


def detect_club(text):
    """
    Match clubs using word boundaries to avoid false positives.
    e.g. 'City' won't match 'Ivory Coast', 'Inter' won't match 'interesting'
    """
    text = text.lower()
    for club, league in TOP_CLUBS.items():
        pattern = r'\b' + re.escape(club) + r'\b'
        if re.search(pattern, text):
            return club.title(), league
    return None, None


def is_relevant(title, summary):

    text = f"{title} {summary}".lower()

    # Filter out non-football content
    banned = ["nfl", "super bowl", "touchdown", "nba", "nhl", "mlb", "cricket", "rugby"]
    if any(b in text for b in banned):
        return False, None, None

    # Club match — highest confidence
    club, league = detect_club(text)
    if club:
        return True, club, league

    # Competition mention
    if any(c in text for c in COMPETITIONS):
        if "bundesliga" in text:
            return True, None, "Bundesliga"
        if "serie a" in text:
            return True, None, "Serie A"
        if "ligue 1" in text:
            return True, None, "Ligue 1"
        if "la liga" in text:
            return True, None, "La Liga"
        if "world cup" in text or "euros" in text or "nations league" in text:
            return True, None, "International"
        return True, None, None

    # General football terms
    if any(g in text for g in GLOBAL_TERMS):
        return True, None, None

    return False, None, None


def parse_timestamp(entry):

    t = entry.get("published_parsed")
    if t:
        try:
            return int(calendar.timegm(t))
        except Exception:
            pass
    return int(time.time())


def generate_club_watch_items():

    items = []
    for club, league in TOP_CLUBS.items():
        # Skip generic international entries
        if league == "International":
            continue
        items.append({
            "title":    f"{club.title()} watch — latest developments",
            "summary":  f"Monitoring {club.title()} in {league}.",
            "category": "football",
            "context":  "club_watch",
            "teams":    [club],
            "league":   league,
            "date":     int(time.time()),
            "query":    f"{club} football match stadium players"
        })
    return items


# --------------------------------------------------
# MAIN FETCH
# --------------------------------------------------

def fetch_news():

    articles = []

    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:

                title   = entry.get("title", "")
                summary = clean_html(entry.get("summary", ""))

                if not title:
                    continue

                relevant, club, league = is_relevant(title, summary)
                if not relevant:
                    continue

                articles.append({
                    "title":    title,
                    "summary":  summary,
                    "category": "football",
                    "context":  "news",
                    "teams":    [club] if club else [],
                    "league":   league if league else "",
                    "date":     parse_timestamp(entry),
                    "query":    f"{title} football match players stadium"
                })
        except Exception as e:
            print(f"Feed error ({url}): {e}")
            continue

    articles += generate_club_watch_items()

    # Deduplicate by exact title
    seen   = set()
    unique = []
    for a in articles:
        key = a["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    return unique[:150]