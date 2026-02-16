def score_article(article):
    title = article.get("title", "").lower()
    category = article.get("category", "")

    score = 0

    # global high-interest keywords
    high = [
        "final", "semi final", "world cup", "grand slam",
        "champions league", "derby", "record", "controversy"
    ]

    # medium importance
    medium = [
        "win", "loss", "defeat", "injury",
        "transfer", "goal", "century"
    ]

    # star power (cross-sport)
    stars = [
        "india", "pakistan",
        "real madrid", "barcelona", "manchester united",
        "djokovic", "nadal", "alcaraz",
        "verstappen", "hamilton"
    ]

    # scoring rules
    for k in high:
        if k in title:
            score += 5

    for k in medium:
        if k in title:
            score += 2

    for k in stars:
        if k in title:
            score += 3

    # category boost
    if category == "cricket":
        score += 2   # India engagement
    elif category == "football":
        score += 2   # global engagement
    elif category == "f1":
        score += 1
    elif category == "tennis":
        score += 1

    return score


def rank_news(articles, top_n=8):
    # attach scores
    for a in articles:
        a["score"] = score_article(a)

    # sort descending
    ranked = sorted(articles, key=lambda x: x["score"], reverse=True)

    # return top N
    return ranked[:top_n]
