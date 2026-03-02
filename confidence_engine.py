import math


# -----------------------------
# HELPERS
# -----------------------------
def form_points(form):
    if not form:
        return 0
    return form.count("W") * 3 + form.count("D")


def goal_diff(gf, ga):
    return (gf or 0) - (ga or 0)


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def compute_confidence(item):

    insight = item.get("insight")

    if not insight:
        item["confidence"] = None
        return item

    home_form = insight.get("home_form", "")
    away_form = insight.get("away_form", "")

    home_points = form_points(home_form)
    away_points = form_points(away_form)

    home_gf = insight.get("home_goals", 0)
    away_gf = insight.get("away_goals", 0)

    home_ga = insight.get("home_conceded", 0)
    away_ga = insight.get("away_conceded", 0)

    # -----------------------------
    # FEATURES
    # -----------------------------
    form_diff = home_points - away_points

    goal_diff_home = goal_diff(home_gf, home_ga)
    goal_diff_away = goal_diff(away_gf, away_ga)

    goal_diff_net = goal_diff_home - goal_diff_away

    home_advantage = 1.2

    score = (
        0.6 * form_diff +
        0.4 * goal_diff_net +
        home_advantage
    )

    # -----------------------------
    # PREDICTION BIAS
    # -----------------------------
    pred = insight.get("prediction")

    if pred == "home_strong":
        score += 1.5
    elif pred == "away_strong":
        score -= 1.5

    # -----------------------------
    # PROBABILITY
    # -----------------------------
    prob_home = sigmoid(score)

    home_pct = int(prob_home * 100)
    away_pct = 100 - home_pct

    # -----------------------------
    # CONFIDENCE LEVEL
    # -----------------------------
    gap = abs(home_pct - away_pct)

    if gap > 30:
        level = "high"
    elif gap > 15:
        level = "medium"
    else:
        level = "low"

    item["confidence"] = {
        "home_pct": home_pct,
        "away_pct": away_pct,
        "level": level
    }

    return item