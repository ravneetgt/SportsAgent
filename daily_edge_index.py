import json
import os
from datetime import datetime

STORE_PATH = "memory_store.json"
HISTORY_PATH = "evi_history.json"


# -----------------------------
# LOADERS
# -----------------------------
def load_store():
    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


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


# -----------------------------
# EVI COMPONENTS
# -----------------------------
def momentum_score(form):
    # recency weighted
    weights = [5, 4, 3, 2, 1]
    form = form[-5:]
    score = 0

    for i, result in enumerate(reversed(form)):
        if result == "W":
            score += weights[i] * 3
        elif result == "D":
            score += weights[i] * 1
        elif result == "L":
            score -= weights[i] * 2

    return score


def control_score(team_data):
    gf = team_data.get("goals_for", 0)
    ga = team_data.get("goals_against", 0)
    return (gf - ga) * 0.5


def instability_score(form):
    # Count swings in last 5 matches
    form = form[-5:]
    swings = 0

    for i in range(1, len(form)):
        if form[i] != form[i-1]:
            swings += 1

    return swings * 1.2


def compute_evi(team_data):

    form = team_data.get("recent_form", [])

    if len(form) < 5:
        return None

    m = momentum_score(form)
    c = control_score(team_data)
    i = instability_score(form)

    evi = (m * 0.5) + (c * 0.3) + (i * 0.2)

    return round(evi, 2)


# -----------------------------
# MAIN GENERATOR
# -----------------------------
def generate_daily_edge_index():

    store = load_store()
    history = load_history()

    today = datetime.utcnow().strftime("%Y-%m-%d")

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

    movement_map = {}
    if yesterday:
        for i, (team, _) in enumerate(yesterday):
            movement_map[team] = i

    lines = []
    biggest_riser = None
    biggest_drop = None
    max_up = -999
    max_down = 999

    for i, (team, score) in enumerate(top5):

        if team in movement_map:
            prev_rank = movement_map[team]
            diff = prev_rank - i

            if diff > 0:
                arrow = "↑"
                if diff > max_up:
                    max_up = diff
                    biggest_riser = team
            elif diff < 0:
                arrow = "↓"
                if diff < max_down:
                    max_down = diff
                    biggest_drop = team
            else:
                arrow = "—"
        else:
            arrow = "NEW"

        lines.append(f"{i+1}. {team} ({score}) {arrow}")

    commentary = ""

    if biggest_riser:
        commentary += f"\nAcceleration: {biggest_riser}."
    if biggest_drop:
        commentary += f"\nVolatility Risk: {biggest_drop}."

    if not commentary:
        commentary = "\nStability can be deceptive."

    history["latest"] = top5
    history[today] = top5
    save_history(history)

    overlay = "GAMETRAIT EVI™"

    final_text = "\n".join(lines) + commentary + "\n\nWho is being overrated?"

    return overlay, final_text