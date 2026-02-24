def score_article(article):
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    category = article.get("category", "")
    context = article.get("context", "general")

    score = 0

    # -----------------------------
    # HIGH-INTEREST (VIRAL)
    # -----------------------------
    high = [
        "final", "semi final", "champions league",
        "derby", "el clasico", "title race",
        "controversy", "ban", "sacked",
        "injury", "red card", "penalty"
    ]

    # -----------------------------
    # MATCH OUTCOMES
    # -----------------------------
    results = [
        "win", "beat", "defeat", "draw",
        "loss", "thrash", "comeback"
    ]

    # -----------------------------
    # TRANSFER / DRAMA
    # -----------------------------
    transfers = [
        "transfer", "bid", "deal", "contract",
        "sign", "exit", "interest", "linked"
    ]

    # -----------------------------
    # BIG CLUBS / STARS
    # -----------------------------
    clubs = [
        "real madrid", "barcelona", "manchester united",
        "man city", "arsenal", "chelsea", "liverpool",
        "psg", "bayern"
    ]

    players = [
        "messi", "ronaldo", "mbappe", "haaland",
        "bellingham", "salah", "de bruyne"
    ]

    # -----------------------------
    # SCORING RULES
    # -----------------------------
    for k in high:
        if k in title:
            score += 5

    for k in results:
        if k in title:
            score += 3

    for k in transfers:
        if k in title:
            score += 4

    for k in clubs:
        if k in title:
            score += 4

    for k in players:
        if k in title:
            score += 3

    # -----------------------------
    # CONTEXT BOOST
    # -----------------------------
    if context == "preview":
        score += 2  # upcoming match interest

    elif context == "result":
        score += 3  # match results perform well

    elif context == "transfer":
        score += 4  # transfers are highly engaging

    # -----------------------------
    # SUMMARY SIGNAL
    # -----------------------------
    if any(k in summary for k in ["controversy", "drama", "tension"]):
        score += 3

    # -----------------------------
    # BASE CATEGORY BOOST
    # -----------------------------
    if category == "football":
        score += 2

    return score


def rank_news(articles, top_n=8):
    for a in articles:
        a["score"] = score_article(a)

    ranked = sorted(articles, key=lambda x: x["score"], reverse=True)

    return ranked[:top_n]
