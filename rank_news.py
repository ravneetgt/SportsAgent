import time


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

BIG_CLUBS = [
    "real madrid", "barcelona", "atletico",
    "manchester city", "manchester united",
    "liverpool", "arsenal", "chelsea", "tottenham",
    "bayern", "dortmund",
    "psg",
    "inter", "milan", "juventus"
]

LOW_VALUE = [
    "quiz", "watch", "tickets", "how to watch",
    "highlights", "fantasy"
]

HIGH_INTENT = [
    "win", "beat", "defeat", "loss", "draw",
    "final", "semi", "derby",
    "transfer", "sign", "bid",
    "injury", "ban", "suspension"
]


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def contains_any(text, keywords):
    return any(k in text for k in keywords)


def club_boost(text):
    """
    Ensures top clubs never disappear from ranking.
    """
    for club in BIG_CLUBS:
        if club in text:
            return 12
    return 0


# --------------------------------------------------
# BASE SCORE
# --------------------------------------------------

def score_article(a):

    title   = a.get("title", "").lower()
    summary = a.get("summary", "").lower()
    context = a.get("context", "news")
    ts      = a.get("date") or a.get("Date")

    text = f"{title} {summary}"

    score = 0

    # --------------------------------------------------
    # LOW VALUE
    # --------------------------------------------------

    if contains_any(title, LOW_VALUE):
        return 0


    # --------------------------------------------------
    # MATCH / FIXTURE
    # --------------------------------------------------

    if " vs " in text:
        score += 8


    # --------------------------------------------------
    # RESULT / EVENTS
    # --------------------------------------------------

    if contains_any(text, HIGH_INTENT):
        score += 10


    # --------------------------------------------------
    # CLUB PRIORITY
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


    # --------------------------------------------------
    # RECENCY
    # --------------------------------------------------

    if ts:
        try:
            age_hours = (time.time() - int(ts)) / 3600

            if age_hours < 3:
                score += 10
            elif age_hours < 12:
                score += 8
            elif age_hours < 24:
                score += 6
            else:
                score += 3

        except Exception:
            score += 3

    else:
        score += 3


    # --------------------------------------------------
    # SHORT TITLE PENALTY
    # --------------------------------------------------

    if len(title) < 40:
        score -= 2


    return max(score, 0)


# --------------------------------------------------
# INSIGHT BOOST
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

    scored = []

    for a in articles:

        s = score_article(a)

        a["score"] = s

        if s > 0:
            scored.append(a)

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)

    return ranked[:top_n]


# --------------------------------------------------
# RE-SCORE AFTER ENRICHMENT
# --------------------------------------------------

def rescore_ranked(articles):

    for a in articles:

        a["score"] = a.get("score", 0) + insight_boost(a)

    return sorted(articles, key=lambda x: x["score"], reverse=True)