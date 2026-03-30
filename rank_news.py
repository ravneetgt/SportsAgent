import re
import time
from difflib import SequenceMatcher


# --------------------------------------------------
# LEAGUE WEIGHTS — only major leagues score above 0
# Anything not listed gets filtered near-out
# --------------------------------------------------

LEAGUE_WEIGHTS = {
    "premier league":   1.0,
    "champions league": 1.0,
    "la liga":          0.9,
    "bundesliga":       0.85,
    "serie a":          0.85,
    "ligue 1":          0.80,
    "europa league":    0.75,
    "international":    0.75,
    "world cup":        1.0,
    "euros":            1.0,
    "nations league":   0.70,
}


# --------------------------------------------------
# CLUB WEIGHTS — higher = more important to surface
# --------------------------------------------------

CLUB_WEIGHTS = {
    "real madrid":          14,
    "barcelona":            14,
    "manchester city":      13,
    "manchester united":    13,
    "liverpool":            13,
    "arsenal":              12,
    "chelsea":              12,
    "bayern":               12,
    "bayern munich":        12,
    "psg":                  12,
    "paris saint germain":  12,
    "inter":                11,
    "inter milan":          11,
    "ac milan":             11,
    "milan":                11,
    "juventus":             11,
    "atletico":             11,
    "atletico madrid":      11,
    "dortmund":             10,
    "borussia dortmund":    10,
    "tottenham":            10,
    "spurs":                10,
    "newcastle":             9,
    "napoli":                9,
    "rb leipzig":            8,
    "leverkusen":            9,
    "bayer leverkusen":      9,
    "marseille":             8,
    "lyon":                  8,
    "monaco":                7,
    "roma":                  8,
    "lazio":                 7,
    "atalanta":              8,
    "aston villa":           8,
    "brighton":              7,
    "west ham":              7,
    "sevilla":               8,
    "villarreal":            7,
}


# --------------------------------------------------
# LOW VALUE — titles matching these get score = 0
# --------------------------------------------------

LOW_VALUE = [
    "quiz",
    "watch live",
    "how to watch",
    "stream online",
    "tickets",
    "highlights",
    "fantasy tips",
    "fpl tips",
    "odds",
    "betting",
    "prediction tips",
]


# --------------------------------------------------
# HIGH INTENT — strong football signal
# --------------------------------------------------

HIGH_INTENT = [
    "win", "beat", "defeat", "loss", "draw",
    "final", "semi-final", "quarter-final",
    "derby", "title", "trophy", "champion",
    "transfer", "sign", "signs", "signed", "signing",
    "bid", "fee", "record", "release clause",
    "injury", "injured", "ban", "suspension",
    "sacked", "appointed", "manager",
    "hat-trick", "goal", "penalty", "red card",
]


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def contains_any(text, keywords):
    return any(k in text for k in keywords)


def club_boost(text):
    """
    Returns score boost based on which club is mentioned.
    Uses word boundary matching — 'City' won't match 'Ivory Coast',
    'Inter' won't match 'interesting', 'Milan' won't match 'Milan Kundera'.
    Returns the highest single club weight found (no double-counting).
    """
    best = 0
    for club, weight in CLUB_WEIGHTS.items():
        pattern = r'\b' + re.escape(club) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            best = max(best, weight)
    return best


def league_boost(article):
    """
    Returns score boost based on the article's tagged league.
    Returns 0 for unknown/small leagues — effectively filters them out.
    """
    league = article.get("league", "").lower()
    weight = LEAGUE_WEIGHTS.get(league, 0)
    return int(weight * 5)


def deduplicate(articles, threshold=0.72):
    """
    Remove near-duplicate articles — same story from multiple sources.
    e.g. BBC + Guardian both covering the same Arsenal result.
    """
    seen, unique = [], []
    for a in articles:
        title = a.get("title", "").lower()
        if not any(SequenceMatcher(None, title, s).ratio() > threshold for s in seen):
            unique.append(a)
            seen.append(title)
    return unique


# --------------------------------------------------
# BASE SCORE
# --------------------------------------------------

def score_article(a):

    title   = a.get("title",   "").lower()
    summary = a.get("summary", "").lower()
    context = a.get("context", "news")
    ts      = a.get("date") or a.get("Date")
    text    = f"{title} {summary}"

    score = 0

    # --------------------------------------------------
    # FILTER: unknown/small leagues score 0
    # --------------------------------------------------
    league = a.get("league", "").lower()
    if league and league not in LEAGUE_WEIGHTS:
        return 0

    # --------------------------------------------------
    # FILTER: low-value titles score 0
    # --------------------------------------------------
    if contains_any(title, LOW_VALUE):
        return 0

    # --------------------------------------------------
    # MATCH / FIXTURE
    # --------------------------------------------------
    if " vs " in text or " v " in text:
        score += 8

    # --------------------------------------------------
    # HIGH INTENT KEYWORDS
    # --------------------------------------------------
    if contains_any(text, HIGH_INTENT):
        score += 10

    # --------------------------------------------------
    # CLUB PRIORITY — word-boundary matched
    # --------------------------------------------------
    score += club_boost(text)

    # --------------------------------------------------
    # CONTEXT
    # --------------------------------------------------
    if context == "preview":
        score += 6
    elif context == "result":
        score += 8
    elif context == "news":
        score += 4
    elif context == "club_watch":
        score += 2

    # --------------------------------------------------
    # RECENCY — articles decay in value over time
    # --------------------------------------------------
    if ts:
        try:
            age_hours = (time.time() - int(ts)) / 3600
            if age_hours < 2:
                score += 12
            elif age_hours < 6:
                score += 10
            elif age_hours < 12:
                score += 7
            elif age_hours < 24:
                score += 4
            else:
                score += 1
        except Exception:
            score += 3
    else:
        score += 3

    # --------------------------------------------------
    # SHORT TITLE PENALTY
    # --------------------------------------------------
    if len(title) < 30:
        score -= 3

    return max(score, 0)


# --------------------------------------------------
# INSIGHT BOOST (applied after enrichment)
# --------------------------------------------------

def insight_boost(a):

    insight = a.get("insight")
    if not insight:
        return 0

    boost = 0

    prediction = insight.get("prediction")
    if prediction in ["home_strong", "away_strong"]:
        boost += 6
    elif prediction == "balanced":
        boost += 3

    if insight.get("home_goals", 0) + insight.get("away_goals", 0) > 8:
        boost += 3

    return boost


# --------------------------------------------------
# INITIAL RANKING
# --------------------------------------------------

def rank_news(articles, top_n=30):

    # Step 1: remove near-duplicates
    articles = deduplicate(articles)

    # Step 2: score each article
    scored = []
    for a in articles:
        base  = score_article(a)
        extra = league_boost(a)
        a["score"] = base + extra
        if a["score"] > 0:
            scored.append(a)

    # Step 3: sort and return top N
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


# --------------------------------------------------
# RE-SCORE AFTER ENRICHMENT
# --------------------------------------------------

def rescore_ranked(articles):
    """
    Apply insight boost after intelligence enrichment.
    Does NOT re-run score_article (avoids double-counting).
    """
    for a in articles:
        a["score"] = a.get("score", 0) + insight_boost(a)
    return sorted(articles, key=lambda x: x["score"], reverse=True)