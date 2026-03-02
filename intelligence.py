import requests
import os

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

team_cache = {}


def api_get(endpoint):
    headers = {"X-Auth-Token": API_KEY}

    try:
        res = requests.get(BASE_URL + endpoint, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("API error:", e)

    return None


def get_team_id(team_name):
    if team_name in team_cache:
        return team_cache[team_name]

    data = api_get("/teams")

    if not data:
        return None

    for team in data.get("teams", []):
        if team_name.lower() in team["name"].lower():
            team_cache[team_name] = team["id"]
            return team["id"]

    return None


def get_team_form(team_id):
    data = api_get(f"/teams/{team_id}/matches?limit=5")

    if not data:
        return None

    matches = data.get("matches", [])

    form = []
    goals_for = 0
    goals_against = 0

    for m in matches:
        score = m.get("score", {}).get("fullTime", {})

        if score.get("home") is None:
            continue

        is_home = m["homeTeam"]["id"] == team_id

        if is_home:
            gf, ga = score["home"], score["away"]
        else:
            gf, ga = score["away"], score["home"]

        goals_for += gf
        goals_against += ga

        if gf > ga:
            form.append("W")
        elif gf == ga:
            form.append("D")
        else:
            form.append("L")

    return {
        "form": "".join(form),
        "goals_for": goals_for,
        "goals_against": goals_against
    }


def predict(home_form, away_form):

    def score(form):
        return form.count("W") * 3 + form.count("D")

    home_score = score(home_form)
    away_score = score(away_form)

    if home_score > away_score + 2:
        return "home_strong"
    elif away_score > home_score + 2:
        return "away_strong"
    else:
        return "balanced"


def enrich_item(item):

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

    prediction = predict(home_form["form"], away_form["form"])

    item["insight"] = {
        "home_team": home,
        "away_team": away,
        "home_form": home_form["form"],
        "away_form": away_form["form"],
        "home_goals": home_form["goals_for"],
        "away_goals": away_form["goals_for"],
        "home_conceded": home_form["goals_against"],
        "away_conceded": away_form["goals_against"],
        "prediction": prediction
    }

    return item