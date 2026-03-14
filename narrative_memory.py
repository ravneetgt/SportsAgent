import json
import os
import hashlib
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
            json.dump(store, f, indent=2)
    except Exception as e:
        print("Memory save error:", e)


# -----------------------------
# CANONICAL TEAM RECORD
# Shared schema used by all modules that write to memory_store.json.
# team_intelligence_engine.py and daily_edge_index.py should also
# conform to this shape — only write keys defined here.
# -----------------------------
def blank_team():
    return {
        "recent_form":      [],   # list of "W"/"D"/"L" — from API data only
        "goals_for":        0,    # from API match data only
        "goals_against":    0,    # from API match data only
        "mention_count":    0,    # incremented on every news mention
        "last_seen":        None, # ISO timestamp of most recent mention
        "last_insight_hash": None # fingerprint of last written insight — prevents re-adding same matches
    }


# -----------------------------
# TEAM EXTRACTION (fallback for news items with no teams field)
# -----------------------------
COMMON_TEAMS = [
    "Arsenal", "Chelsea", "Liverpool", "Manchester City",
    "Manchester United", "Tottenham", "Barcelona",
    "Real Madrid", "Bayern", "Inter", "Milan",
    "Juventus", "PSG", "Atletico Madrid", "Dortmund"
]


def extract_teams_from_title(title):
    found = []
    for team in COMMON_TEAMS:
        if team.lower() in title.lower():
            found.append(team)
    if len(found) >= 2:
        return found[:2]
    return None


# -----------------------------
# INSIGHT FINGERPRINT
# Hashes the match data fields that represent actual results.
# If the same fixture is processed again (same run or next day before
# new matches), the hash matches and we skip the write.
# -----------------------------
def insight_hash(insight, prefix):
    key = f"{insight.get(f'{prefix}_form', '')}|{insight.get(f'{prefix}_goals', 0)}|{insight.get(f'{prefix}_conceded', 0)}"
    return hashlib.md5(key.encode()).hexdigest()


# -----------------------------
# UPDATE MEMORY
# -----------------------------
def update_memory(item):
    store = load_store()

    teams = item.get("teams")
    if not teams:
        teams = extract_teams_from_title(item.get("title", ""))

    if not teams:
        return

    # Normalise to exactly 2
    if len(teams) == 1:
        teams = [teams[0], teams[0]]
    teams = teams[:2]

    home, away = teams

    # Ensure both teams have a record
    for team in [home, away]:
        if team not in store:
            store[team] = blank_team()
        else:
            # Backfill any keys missing from older records
            for k, v in blank_team().items():
                store[team].setdefault(k, v)

    insight = item.get("insight")
    now = str(datetime.utcnow())

    if insight:
        # --------------------------------------------------
        # STRUCTURED UPDATE — from fixture enrichment only.
        # Uses insight fingerprint to skip duplicate writes.
        # Never called for news items (they have no insight).
        # --------------------------------------------------
        for team, prefix in [(home, "home"), (away, "away")]:
            team_data = store[team]

            h = insight_hash(insight, prefix)

            if team_data.get("last_insight_hash") == h:
                # Same match data as last time — don't re-add
                continue

            form_str = insight.get(f"{prefix}_form", "")
            gf       = insight.get(f"{prefix}_goals", 0)
            ga       = insight.get(f"{prefix}_conceded", 0)

            # Replace recent_form with API data (source of truth)
            new_form = list(form_str)
            existing = team_data.get("recent_form", [])
            team_data["recent_form"] = (existing + new_form)[-10:]

            # Only update goal tallies when insight is new
            team_data["goals_for"]      += gf
            team_data["goals_against"]  += ga

            team_data["last_insight_hash"] = h
            team_data["last_seen"]         = now

            store[team] = team_data

    else:
        # --------------------------------------------------
        # LIGHTWEIGHT UPDATE — news mention only.
        # Increments mention counter and timestamps last_seen.
        # Does NOT touch recent_form, goals, or match counts —
        # those fields must only come from verified match data.
        # --------------------------------------------------
        for team in [home, away]:
            store[team]["mention_count"] = store[team].get("mention_count", 0) + 1
            store[team]["last_seen"]     = now

    save_store(store)


# -----------------------------
# BUILD NARRATIVE
# Reads from memory to build context strings for caption generation.
# Only generates narrative when form data is from real matches (has
# at least 5 entries populated via structured updates).
# -----------------------------
def get_narrative(item):
    store = load_store()

    teams = item.get("teams")
    if not teams:
        teams = extract_teams_from_title(item.get("title", ""))

    if not teams:
        return ""

    narratives = []

    for team in teams:
        data = store.get(team)
        if not data:
            continue

        form = data.get("recent_form", [])
        if len(form) < 5:
            continue

        last5  = form[-5:]
        wins   = last5.count("W")
        losses = last5.count("L")

        gf = data.get("goals_for", 0)
        ga = data.get("goals_against", 0)

        if wins >= 4:
            narratives.append(f"{team} are building momentum")

        if losses >= 3:
            narratives.append(f"{team} are struggling for stability")

        if gf > 0 and ga > gf:
            narratives.append(f"{team} are conceding more than they control")

        if gf > ga + 5:
            narratives.append(f"{team} are creating consistent attacking pressure")

        mentions = data.get("mention_count", 0)
        if mentions >= 5 and wins >= 3:
            narratives.append(f"{team} are generating significant attention right now")

    return ". ".join(narratives)
