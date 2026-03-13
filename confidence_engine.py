import math
from prediction_learning import get_weights


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def form_points(form):

    if not form:
        return 0

    return form.count("W") * 3 + form.count("D")


def compute_confidence(item):

    insight = item.get("insight")

    if not insight:
        item["confidence"] = None
        return item

    form_weight, goal_weight, home_advantage = get_weights()

    home_form = insight.get("home_form", "")
    away_form = insight.get("away_form", "")

    home_points = form_points(home_form)
    away_points = form_points(away_form)

    home_gf = insight.get("home_goals", 0)
    away_gf = insight.get("away_goals", 0)

    home_ga = insight.get("home_conceded", 0)
    away_ga = insight.get("away_conceded", 0)

    form_diff = home_points - away_points

    goal_diff_home = home_gf - home_ga
    goal_diff_away = away_gf - away_ga

    goal_diff_net = goal_diff_home - goal_diff_away

    score = (
        form_weight * form_diff +
        goal_weight * goal_diff_net +
        home_advantage
    )

    prob_home = sigmoid(score)

    home_pct = int(prob_home * 100)
    away_pct = 100 - home_pct

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