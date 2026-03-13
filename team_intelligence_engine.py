import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

STORE_PATH = "memory_store.json"


def api_get(endpoint):

    headers = {"X-Auth-Token": API_KEY}

    try:
        res = requests.get(BASE_URL + endpoint, headers=headers, timeout=10)

        if res.status_code == 200:
            return res.json()

    except Exception as e:
        print("API error:", e)

    return None


def load_store():

    if not os.path.exists(STORE_PATH):
        return {}

    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_store(store):

    try:
        with open(STORE_PATH, "w") as f:
            json.dump(store, f)
    except Exception as e:
        print("Save error:", e)


def update_team(team_id, team_name):

    data = api_get(f"/teams/{team_id}/matches?limit=10")

    if not data:
        return None

    matches = data.get("matches", [])

    form = []
    gf = 0
    ga = 0

    for m in matches:

        score = m.get("score", {}).get("fullTime", {})

        if score.get("home") is None:
            continue

        is_home = m["homeTeam"]["id"] == team_id

        if is_home:
            goals_for = score["home"]
            goals_against = score["away"]
        else:
            goals_for = score["away"]
            goals_against = score["home"]

        gf += goals_for
        ga += goals_against

        if goals_for > goals_against:
            form.append("W")
        elif goals_for == goals_against:
            form.append("D")
        else:
            form.append("L")

    return {
        "team": team_name,
        "recent_form": form,
        "goals_for": gf,
        "goals_against": ga,
        "updated": str(datetime.utcnow())
    }


def refresh_teams():

    store = load_store()

    teams = api_get("/teams")

    if not teams:
        return

    for team in teams.get("teams", [])[:40]:

        name = team["name"]
        tid = team["id"]

        print("Updating", name)

        data = update_team(tid, name)

        if data:
            store[name] = data

    save_store(store)