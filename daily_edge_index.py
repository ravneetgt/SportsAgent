import json
import os
from datetime import datetime
import requests

STORE_PATH = "memory_store.json"
HISTORY_PATH = "evi_history.json"

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

CORE_TEAMS = [
    "Real Madrid",
    "Barcelona",
    "Manchester City",
    "Arsenal",
    "Liverpool",
    "Chelsea",
    "Bayern Munich",
    "PSG",
    "Inter",
    "AC Milan"
]


def api_get(endpoint):

    headers = {"X-Auth-Token": API_KEY}

    try:
        r = requests.get(BASE_URL + endpoint, headers=headers, timeout=10)

        if r.status_code == 200:
            return r.json()

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
    except:
        pass


def load_history():

    if not os.path.exists(HISTORY_PATH):
        return {}

    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_history(data):

    try:
        with open(HISTORY_PATH, "w") as f:
            json.dump(data, f)
    except:
        pass


def fetch_team_data(team_name):

    teams = api_get("/teams")

    if not teams:
        return None

    team_id = None

    for t in teams.get("teams", []):
        if team_name.lower() in t["name"].lower():
            team_id = t["id"]
            break

    if not team_id:
        return None

    matches = api_get(f"/teams/{team_id}/matches?limit=10")

    if not matches:
        return None

    form = []
    gf = 0
    ga = 0

    for m in matches.get("matches", []):

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
        "recent_form": form,
        "goals_for": gf,
        "goals_against": ga
    }


def momentum_score(form):

    weights = [5, 4, 3, 2, 1]
    form = form[-5:]

    score = 0

    for i, result in enumerate(reversed(form)):

        if result == "W":
            score += weights[i] * 3
        elif result == "D":
            score += weights[i]
        elif result == "L":
            score -= weights[i] * 2

    return score


def control_score(team):

    gf = team.get("goals_for", 0)
    ga = team.get("goals_against", 0)

    return (gf - ga) * 0.5


def instability_score(form):

    swings = 0

    for i in range(1, len(form)):
        if form[i] != form[i - 1]:
            swings += 1

    return swings * 1.2


def compute_evi(team):

    form = team.get("recent_form", [])

    if len(form) < 5:
        return None

    momentum = momentum_score(form)
    control = control_score(team)
    instability = instability_score(form)

    evi = (
        momentum * 0.5 +
        control * 0.3 +
        instability * 0.2
    )

    return round(evi, 2)


def generate_daily_edge_index():

    store = load_store()
    history = load_history()

    for team in CORE_TEAMS:

        if team not in store:

            print("Fetching missing team:", team)

            data = fetch_team_data(team)

            if data:
                store[team] = data

    save_store(store)

    scores = []

    for team, data in store.items():

        evi = compute_evi(data)

        if evi is not None:
            scores.append((team, evi))

    if not scores:
        return None, None, None

    scores.sort(key=lambda x: x[1], reverse=True)

    top5 = scores[:5]

    # -------- VISUAL TEXT FOR INSTAGRAM CARD --------

    visual_lines = []

    for i, (team, score) in enumerate(top5):

        visual_lines.append(f"{i+1}. {team:<15} {score}")

    visual_text = "\n".join(visual_lines)

    # -------- CAPTION TEXT --------

    caption_lines = []

    for i, (team, score) in enumerate(top5):
        caption_lines.append(f"{i+1}. {team} ({score})")

    caption = "\n".join(caption_lines)

    caption += "\n\nThe Edge Volatility Index measures momentum, control and instability across elite clubs."

    # -------- ARTICLE --------

    leader = top5[0][0]

    article = f"""
The Gametrait Edge Volatility Index tracks which clubs currently hold the strongest competitive momentum.

Unlike traditional standings, the EVI blends recent form, goal control and volatility patterns to detect where pressure and momentum are building across elite European teams.

Today's leader is {leader}, whose recent performances place them at the top of the volatility model.

Momentum indicators suggest several clubs are beginning to separate from the pack, while instability signals reveal which teams may be entering unpredictable phases.

By tracking volatility rather than simply results, the index often surfaces shifts in competitive power before they appear in league tables.
"""

    history["latest"] = top5
    history[datetime.utcnow().strftime("%Y-%m-%d")] = top5

    save_history(history)

    overlay = "EDGE VOLATILITY INDEX"

    return overlay, visual_text, caption, article