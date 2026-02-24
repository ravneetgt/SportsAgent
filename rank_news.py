def score_article(a):
    t = a["title"].lower()
    score = 0

    if "vs" in t:
        score += 3
    if "transfer" in t:
        score += 4
    if "final" in t or "derby" in t:
        score += 5

    big_clubs = ["real madrid", "barcelona", "manchester", "liverpool", "arsenal"]
    if any(c in t for c in big_clubs):
        score += 3

    return score


def rank_news(articles):
    for a in articles:
        a["score"] = score_article(a)

    articles = sorted(articles, key=lambda x: x["score"], reverse=True)
    return articles[:10]