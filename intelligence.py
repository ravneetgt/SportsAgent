from football_api import get_team_id, get_team_form
from team_metrics import form_points


def _form_verdict(home_form: str, away_form: str) -> str:
    """Simple form-based prediction used as early ranking signal in rank_news."""
    h = form_points(list(home_form))
    a = form_points(list(away_form))

    if h > a + 2:
        return "home_strong"
    elif a > h + 2:
        return "away_strong"
    return "balanced"


def enrich_item(item: dict) -> dict:
    """
    Adds insight data to fixture preview items.
    News items (context != 'preview') pass through unchanged.
    Idempotent — if insight already set, returns item immediately.
    """
    if item.get("insight"):
        return item

    if item.get("context") != "preview":
        return item

    teams = item.get("teams")
    if not teams or len(teams) != 2:
        return item

    home, away = teams

    home_id = get_team_id(home)
    away_id = get_team_id(away)

    if not home_id or not away_id:
        return item

    home_form = get_team_form(home_id)
    away_form = get_team_form(away_id)

    if not home_form or not away_form:
        return item

    item["insight"] = {
        "home_team":    home,
        "away_team":    away,
        "home_form":    home_form["form"],
        "away_form":    away_form["form"],
        "home_goals":   home_form["goals_for"],
        "away_goals":   away_form["goals_for"],
        "home_conceded": home_form["goals_against"],
        "away_conceded": away_form["goals_against"],
        "prediction":   _form_verdict(home_form["form"], away_form["form"])
    }

    return item