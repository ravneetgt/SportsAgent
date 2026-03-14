import math
from team_metrics import form_points
from prediction_learning import get_weights


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def compute_confidence(item: dict) -> dict:
    insight = item.get("insight")

    if not insight:
        item["confidence"] = None
        return item

    form_weight, goal_weight, home_advantage = get_weights()

    home_points = form_points(list(insight.get("home_form", "")))
    away_points = form_points(list(insight.get("away_form", "")))

    goal_diff_net = (
        (insight.get("home_goals", 0) - insight.get("home_conceded", 0)) -
        (insight.get("away_goals", 0) - insight.get("away_conceded", 0))
    )

    score     = form_weight * (home_points - away_points) + goal_weight * goal_diff_net + home_advantage
    prob_home = sigmoid(score)

    home_pct  = int(prob_home * 100)
    away_pct  = 100 - home_pct
    gap       = abs(home_pct - away_pct)

    level = "high" if gap > 30 else "medium" if gap > 15 else "low"

    item["confidence"] = {
        "home_pct": home_pct,
        "away_pct": away_pct,
        "level":    level
    }

    return item