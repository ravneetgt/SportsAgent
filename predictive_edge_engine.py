import json
from team_metrics import form_points, volatility

STORE_PATH = "memory_store.json"


def load_store():
    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def goal_control(team):

    gf = team.get("goals_for", 0)
    ga = team.get("goals_against", 0)

    if gf + ga == 0:
        return 0

    return gf / (gf + ga)


def compute_edge(home_team, away_team, confidence=None):

    store = load_store()

    home = store.get(home_team)
    away = store.get(away_team)

    if not home or not away:
        return None

    home_form = home.get("recent_form", [])
    away_form = away.get("recent_form", [])

    home_points = form_points(home_form)
    away_points = form_points(away_form)

    form_edge = home_points - away_points

    home_control = goal_control(home)
    away_control = goal_control(away)

    control_edge = home_control - away_control

    home_vol = volatility(home_form)
    away_vol = volatility(away_form)

    volatility_edge = away_vol - home_vol

    edge_score = (
        (form_edge * 0.6) +
        (control_edge * 4) +
        (volatility_edge * 0.4)
    )

    if confidence:

        home_pct = confidence.get("home_pct", 50)
        away_pct = confidence.get("away_pct", 50)

        prob_edge = (home_pct - away_pct) / 10
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
        "home": home_team,
        "away": away_team,
        "edge_score": edge_score,
        "verdict": verdict
    }