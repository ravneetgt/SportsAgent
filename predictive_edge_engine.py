from team_metrics import form_points, volatility
from store import load_store


def goal_control(team: dict) -> float:
    gf = team.get("goals_for", 0)
    ga = team.get("goals_against", 0)

    if gf + ga == 0:
        return 0

    return gf / (gf + ga)


def compute_edge(home_team: str, away_team: str, confidence: dict = None) -> dict | None:
    store = load_store()

    home = store.get(home_team)
    away = store.get(away_team)

    if not home or not away:
        return None

    home_form = home.get("recent_form", [])
    away_form = away.get("recent_form", [])

    form_edge      = form_points(home_form) - form_points(away_form)
    control_edge   = goal_control(home) - goal_control(away)
    volatility_edge = volatility(away_form) - volatility(home_form)

    edge_score = (
        (form_edge       * 0.6) +
        (control_edge    * 4.0) +
        (volatility_edge * 0.4)
    )

    if confidence:
        prob_edge   = (confidence.get("home_pct", 50) - confidence.get("away_pct", 50)) / 10
        edge_score += prob_edge

    edge_score = round(edge_score, 2)

    if edge_score > 3:
        verdict = f"{home_team} strong edge"
    elif edge_score > 1:
        verdict = f"{home_team} slight edge"
    elif edge_score < -3:
        verdict = f"{away_team} strong edge"
    elif edge_score < -1:
        verdict = f"{away_team} slight edge"
    else:
        verdict = "balanced matchup"

    return {
        "home":       home_team,
        "away":       away_team,
        "edge_score": edge_score,
        "verdict":    verdict
    }