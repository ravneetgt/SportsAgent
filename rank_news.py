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
# SCORING
# -----------------------------
def score_article(a):

    title = a.get("title", "").lower()
    summary = a.get("summary", "").lower()
    context = a.get("context", "news")
    ts = a.get("date") or a.get("Date")

    text = f"{title} {summary}"

    score = 0

    # -----------------------------
    # LOW VALUE FILTER
    # -----------------------------
    if contains_any(title, LOW_VALUE):
        return 0  # kill it

    # -----------------------------
    # MATCH / FIXTURE
    # -----------------------------
    if " vs " in text:
        score += 6

    # -----------------------------
    # RESULT / EVENT
    # -----------------------------
    if contains_any(text, HIGH_INTENT):
        score += 8

    # -----------------------------
    # BIG CLUBS
    # -----------------------------
    if any(c in text for c in BIG_CLUBS):
        score += 6

    # -----------------------------
    # CONTEXT BOOST
    # -----------------------------
    if context == "preview":
        score += 6
    elif context == "news":
        score += 4

    # -----------------------------
    # INTELLIGENCE BOOST
    # -----------------------------
    insight = a.get("insight")

    if insight:
        prediction = insight.get("prediction")

        if prediction in ["home_strong", "away_strong"]:
            score += 6
        elif prediction == "balanced":
            score += 3

        # high scoring teams
        if insight.get("home_goals", 0) + insight.get("away_goals", 0) > 8:
            score += 3

    # -----------------------------
    # RECENCY BOOST
    # -----------------------------
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
        except:
            score += 3

    else:
        score += 3

    # -----------------------------
    # PENALISE GENERIC
    # -----------------------------
    if len(title) < 40:
        score -= 2

    # clamp
    return max(score, 0)


# -----------------------------
# RANKING
# -----------------------------
def rank_news(articles, top_n=15):

    scored = []

    for a in articles:
        s = score_article(a)
        a["score"] = s

        if s > 0:  # filter junk
            scored.append(a)

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)

    return ranked[:top_n]