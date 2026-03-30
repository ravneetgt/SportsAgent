import math
from team_metrics import form_points
from prediction_learning import get_weights


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def compute_confidence(item: dict) -> dict:
    """
    Computes match confidence for fixture previews.

    Adds to item:
      confidence.home_pct   — int 0-100
      confidence.away_pct   — int 0-100
      confidence.level      — "high" / "medium" / "low"
      confidence.label      — human-readable e.g. "68% — HIGH CONFIDENCE"
      confidence.summary    — one-line verdict e.g. "Arsenal favoured (68% vs 32%)"
    """
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

    score     = (form_weight * (home_points - away_points)
                 + goal_weight * goal_diff_net
                 + home_advantage)
    prob_home = sigmoid(score)

    home_pct = int(prob_home * 100)
    away_pct = 100 - home_pct
    gap      = abs(home_pct - away_pct)

    level = "high" if gap > 30 else "medium" if gap > 15 else "low"

    # Human-readable label
    if level == "high":
        label = f"{max(home_pct, away_pct)}% — HIGH CONFIDENCE"
    elif level == "medium":
        label = f"{max(home_pct, away_pct)}% — MODERATE"
    else:
        label = f"{max(home_pct, away_pct)}% — TOO CLOSE TO CALL"

    # One-line summary for captions/articles
    home_team = insight.get("home_team", "Home")
    away_team = insight.get("away_team", "Away")

    if home_pct > 55:
        summary = f"{home_team} favoured ({home_pct}% vs {away_pct}%)"
    elif away_pct > 55:
        summary = f"{away_team} favoured ({away_pct}% vs {home_pct}%)"
    else:
        summary = f"Too close to call — {home_pct}% vs {away_pct}%"

    item["confidence"] = {
        "home_pct": home_pct,
        "away_pct": away_pct,
        "level":    level,
        "label":    label,     # e.g. "68% — HIGH CONFIDENCE"
        "summary":  summary,   # e.g. "Arsenal favoured (68% vs 32%)"
    }

    return item