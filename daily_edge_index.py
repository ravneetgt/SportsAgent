import json
import os
from datetime import datetime
import requests

STORE_PATH = "memory_store.json"
HISTORY_PATH = "evi_history.json"

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

# -------------------------------------
# TEAMS THAT SHOULD ALWAYS BE TRACKED
# -------------------------------------
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


# -------------------------------------
# API HELPER
# -------------------------------------
def api_get(endpoint):

    headers = {"X-Auth-Token": API_KEY}

    try:
        r = requests.get(BASE_URL + endpoint, headers=headers, timeout=10)

        if r.status_code == 200:
            return r.json()

    except Exception as e:
        print("API error:", e)

    return None


# -------------------------------------
# STORE LOADERS
# -------------------------------------
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


# -------------------------------------
# FETCH TEAM DATA IF MISSING
# -------------------------------------
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


# -------------------------------------
# SIGNAL COMPONENTS
# -------------------------------------
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


# -------------------------------------
# EVI CALCULATION
# -------------------------------------
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


# -------------------------------------
# DAILY REPORT
# -------------------------------------
def generate_daily_edge_index():

    store = load_store()
    history = load_history()

    # -------------------------------------
    # ENSURE CORE TEAMS EXIST
    # -------------------------------------
    for team in CORE_TEAMS:

        if team not in store:

            print("Fetching missing team:", team)

            data = fetch_team_data(team)

            if data:
                store[team] = data

    save_store(store)

    # -------------------------------------
    # COMPUTE SCORES
    # -------------------------------------
    scores = []

    for team, data in store.items():

        evi = compute_evi(data)

        if evi is not None:
            scores.append((team, evi))

    if not scores:
        return None, None

    scores.sort(key=lambda x: x[1], reverse=True)

    top5 = scores[:5]

    yesterday = history.get("latest", [])

    deltas = {}

    if yesterday:

        ymap = dict(yesterday)

        for team, score in top5:

            prev = ymap.get(team)

            if prev is not None:
                deltas[team] = round(score - prev, 2)

    # -------------------------------------
    # MOVEMENT DETECTION
    # -------------------------------------
    biggest_up = None
    biggest_down = None

    max_up = -999
    max_down = 999

    for team, delta in deltas.items():

        if delta > max_up:
            max_up = delta
            biggest_up = team

        if delta < max_down:
            max_down = delta
            biggest_down = team

    # -------------------------------------
    # BUILD REPORT
    # -------------------------------------
    lines = []

    for i, (team, score) in enumerate(top5):

        delta = deltas.get(team)

        if delta is None:
            change = "NEW"
        elif delta > 0:
            change = f"+{delta}"
        elif delta < 0:
            change = f"{delta}"
        else:
            change = "0"

        lines.append(f"{i+1}. {team} ({score}) {change}")

    leader = top5[0]

    commentary = []

    commentary.append(f"Edge leader: {leader[0]} ({leader[1]}).")

    if biggest_up:
        commentary.append(f"Momentum surge: {biggest_up} (+{max_up}).")

    if biggest_down:
        commentary.append(f"Volatility risk: {biggest_down} ({max_down}).")

    commentary.append("Momentum shifts reveal where pressure is building.")

    final_text = "\n".join(lines) + "\n\n" + "\n".join(commentary)

    history["latest"] = top5
    history[datetime.utcnow().strftime("%Y-%m-%d")] = top5

    save_history(history)

    overlay = "GAMETRAIT EDGE REPORT"

    return overlay, final_text