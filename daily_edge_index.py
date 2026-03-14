import json
import os
from datetime import datetime

from football_api import api_get, get_team_id
from store import load_store, save_store

HISTORY_PATH = "evi_history.json"

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


# -----------------------------
# HISTORY STORE
# -----------------------------
def load_history() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(data: dict) -> None:
    try:
        with open(HISTORY_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("History save error:", e)


# -----------------------------
# TEAM DATA FETCH
# -----------------------------
def fetch_team_data(team_name: str) -> dict | None:
    team_id = get_team_id(team_name)
    if not team_id:
        return None

    data = api_get(f"/teams/{team_id}/matches?limit=10&status=FINISHED")
    if not data:
        return None

    form = []
    gf   = 0
    ga   = 0

    for m in data.get("matches", []):
        score = m.get("score", {}).get("fullTime", {})

        if score.get("home") is None:
            continue

        is_home       = m["homeTeam"]["id"] == team_id
        goals_for     = score["home"] if is_home else score["away"]
        goals_against = score["away"] if is_home else score["home"]

        gf += goals_for
        ga += goals_against

        if goals_for > goals_against:
            form.append("W")
        elif goals_for == goals_against:
            form.append("D")
        else:
            form.append("L")

    return {"recent_form": form, "goals_for": gf, "goals_against": ga}


# -----------------------------
# EVI SCORING
# -----------------------------
def momentum_score(form: list) -> float:
    weights = [5, 4, 3, 2, 1]
    form    = form[-5:]
    score   = 0

    for i, result in enumerate(reversed(form)):
        if result == "W":
            score += weights[i] * 3
        elif result == "D":
            score += weights[i]
        elif result == "L":
            score -= weights[i] * 2

    return score


def control_score(team: dict) -> float:
    return (team.get("goals_for", 0) - team.get("goals_against", 0)) * 0.5


def instability_score(form: list) -> float:
    swings = sum(1 for i in range(1, len(form)) if form[i] != form[i - 1])
    return swings * 1.2


def compute_evi(team: dict) -> float | None:
    form = team.get("recent_form", [])
    if len(form) < 5:
        return None

    evi = (
        momentum_score(form)    * 0.5 +
        control_score(team)     * 0.3 +
        instability_score(form) * 0.2
    )
    return round(evi, 2)


# -----------------------------
# MAIN
# -----------------------------
def generate_daily_edge_index():
    store   = load_store()
    history = load_history()

    # Fetch any CORE_TEAMS missing from store
    for team in CORE_TEAMS:
        if team not in store:
            print("Fetching missing team:", team)
            data = fetch_team_data(team)
            if data:
                store[team] = data

    save_store(store)

    scores = [
        (team, evi)
        for team, data in store.items()
        if (evi := compute_evi(data)) is not None
    ]

    if not scores:
        return None, None, None, None

    scores.sort(key=lambda x: x[1], reverse=True)
    top5 = scores[:5]

    # Visual text (Instagram card)
    visual_text = "\n".join(
        f"{i+1}. {team:<15} {score}"
        for i, (team, score) in enumerate(top5)
    )

    # Caption
    caption = "\n".join(
        f"{i+1}. {team} ({score})"
        for i, (team, score) in enumerate(top5)
    )
    caption += "\n\nThe Edge Volatility Index measures momentum, control and instability across elite clubs."

    # Article
    leader  = top5[0][0]
    article = (
        f"The Gametrait Edge Volatility Index tracks which clubs currently hold "
        f"the strongest competitive momentum.\n\n"
        f"Unlike traditional standings, the EVI blends recent form, goal control "
        f"and volatility patterns to detect where pressure and momentum are building "
        f"across elite European teams.\n\n"
        f"Today's leader is {leader}, whose recent performances place them at the top "
        f"of the volatility model.\n\n"
        f"Momentum indicators suggest several clubs are beginning to separate from the "
        f"pack, while instability signals reveal which teams may be entering unpredictable phases.\n\n"
        f"By tracking volatility rather than simply results, the index often surfaces "
        f"shifts in competitive power before they appear in league tables."
    )

    today = datetime.utcnow().strftime("%Y-%m-%d")
    history["latest"] = top5
    history[today]    = top5
    save_history(history)

    return "EDGE VOLATILITY INDEX", visual_text, caption, article