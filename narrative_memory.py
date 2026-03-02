import json
import os
from datetime import datetime

STORE_PATH = "memory_store.json"


# -----------------------------
# LOAD / SAVE
# -----------------------------
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
        print("Memory save error:", e)


# -----------------------------
# UPDATE MEMORY
# -----------------------------
def update_memory(item):

    store = load_store()

    insight = item.get("insight")
    teams = item.get("teams")

    # Only update if we have teams
    if not teams or len(teams) != 2:
        return

    home, away = teams

    for team in [home, away]:
        if team not in store:
            store[team] = {
                "matches": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "goals_for": 0,
                "goals_against": 0,
                "recent_form": [],
                "last_updated": str(datetime.utcnow())
            }

    # -----------------------------
    # UPDATE USING INSIGHT
    # -----------------------------
    if insight:

        # Approximate trends from last 5 matches
        for team, prefix in [(home, "home"), (away, "away")]:
            team_data = store.get(team)

            form = insight.get(f"{prefix}_form", "")
            gf = insight.get(f"{prefix}_goals", 0)
            ga = insight.get(f"{prefix}_conceded", 0)

            if not team_data:
                continue

            # Update totals
            team_data["matches"] += len(form)
            team_data["wins"] += form.count("W")
            team_data["draws"] += form.count("D")
            team_data["losses"] += form.count("L")

            team_data["goals_for"] += gf
            team_data["goals_against"] += ga

            # Track last results
            team_data["recent_form"] = (team_data["recent_form"] + list(form))[-10:]

            team_data["last_updated"] = str(datetime.utcnow())

            store[team] = team_data

    save_store(store)


# -----------------------------
# BUILD NARRATIVE
# -----------------------------
def get_narrative(item):

    store = load_store()

    teams = item.get("teams")

    if not teams or len(teams) != 2:
        return ""

    home, away = teams

    narratives = []

    for team in [home, away]:

        data = store.get(team)

        if not data:
            continue

        form = data.get("recent_form", [])

        if len(form) < 5:
            continue

        last5 = form[-5:]

        wins = last5.count("W")
        losses = last5.count("L")

        gf = data.get("goals_for", 0)
        ga = data.get("goals_against", 0)

        # -----------------------------
        # PATTERNS
        # -----------------------------
        if wins >= 4:
            narratives.append(f"{team} are building momentum")

        if losses >= 3:
            narratives.append(f"{team} are struggling for stability")

        if ga > gf:
            narratives.append(f"{team} are conceding more than they control")

        if gf > ga + 5:
            narratives.append(f"{team} are creating consistent attacking pressure")

    return ". ".join(narratives)