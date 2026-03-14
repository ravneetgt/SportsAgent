import time

# -----------------------------
# CONFIG
# -----------------------------
BIG_CLUBS = [
    "real madrid", "barcelona", "manchester", "liverpool",
    "arsenal", "chelsea", "psg", "bayern", "inter", "milan"
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


# -----------------------------
# HELPERS
# -----------------------------
def contains_any(text, keywords):
    return any(k in text for k in keywords)


# -----------------------------
# BASE SCORE
# Used before enrichment — no insight available yet.
# -----------------------------
def score_article(a):

    title   = a.get("title", "").lower()
    summary = a.get("summary", "").lower()
    context = a.get("context", "news")
    ts      = a.get("date") or a.get("Date")

    text = f"{title} {summary}"

    score = 0

    # Low value filter
    if contains_any(title, LOW_VALUE):
        return 0

    # Match / fixture
    if " vs " in text:
        score += 6

    # Result / event keywords
    if contains_any(text, HIGH_INTENT):
        score += 8

    # Big clubs
    if any(c in text for c in BIG_CLUBS):
        score += 6

    # Context
    if context == "preview":
        score += 6
    elif context == "news":
        score += 4

    # Recency — now works for news items because fetch_news.py
    # populates the "date" field from feedparser's published_parsed
    if ts:
        try:
            age_hours = (time.time() - int(ts)) / 3600

            if age_hours < 3:
                score += 10
            elif age_hours < 12:
                score += 8
            elif age_hours < 24:
                score += 5
            else:
                score += 2
        except Exception:
            score += 3
    else:
        score += 3

    # Penalise very short titles (usually generic)
    if len(title) < 40:
        score -= 2

    return max(score, 0)


# -----------------------------
# INSIGHT BOOST
# Applied separately after enrich_item() has run in main.py.
# Keeps ranking logic honest — scores only reflect real data.
# -----------------------------
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


# -----------------------------
# INITIAL RANKING (pre-enrichment)
# Called in main.py before process_item loop.
# -----------------------------
def rank_news(articles, top_n=15):
    scored = []

    for a in articles:
        s = score_article(a)
        a["score"] = s

        if s > 0:
            scored.append(a)

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


# -----------------------------
# RE-SCORE (post-enrichment)
# Call this in main.py after enrich_item() on fixtures,
# before processing, to apply insight boosts.
#
# Usage in main.py:
#   ranked = rank_news(all_content)
#   ranked = rescore_ranked(ranked)
#   for item in ranked: process_item(item)
# -----------------------------
def rescore_ranked(articles):
    for a in articles:
        a["score"] = a.get("score", 0) + insight_boost(a)

    return sorted(articles, key=lambda x: x["score"], reverse=True)
