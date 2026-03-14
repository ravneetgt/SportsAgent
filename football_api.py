"""
football_api.py
---------------
Single source for all football-data.org v4 API access.
Uses only free-tier endpoints:
  /teams                       — full team list for ID lookup
  /teams/{id}/matches?limit=N  — recent matches for form data

/competitions/{comp}/teams requires a paid plan and is NOT used here.
"""

import os
import time
import requests

API_KEY  = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"

# In-process cache — populated once per pipeline run
_team_cache: dict = {}
_teams_loaded: bool = False


# -----------------------------
# CORE REQUEST — with retry
# -----------------------------
def api_get(endpoint: str, retries: int = 3):
    headers = {"X-Auth-Token": API_KEY}

    for attempt in range(retries):
        try:
            res = requests.get(
                BASE_URL + endpoint,
                headers=headers,
                timeout=10
            )

            if res.status_code == 200:
                return res.json()

            if res.status_code == 429:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue

            # Don't retry on auth or not-found errors — they won't resolve
            if res.status_code in (400, 401, 403, 404):
                print(f"API {res.status_code} on {endpoint}")
                return None

            print(f"API {res.status_code} on {endpoint} (attempt {attempt + 1})")

        except Exception as e:
            print(f"API error (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    return None


# -----------------------------
# TEAM ID LOOKUP
# Loads /teams once and caches name → id for the run.
# -----------------------------
def _load_team_cache():
    global _teams_loaded
    if _teams_loaded:
        return

    data = api_get("/teams")
    if not data:
        print("football_api: could not load team list")
        _teams_loaded = True
        return

    for t in data.get("teams", []):
        name = t.get("name", "")
        tid  = t.get("id")
        if name and tid:
            _team_cache[name.lower()] = tid

    _teams_loaded = True


def get_team_id(team_name: str):
    """Returns football-data.org team ID for team_name, or None."""
    _load_team_cache()
    needle = team_name.lower()

    # Exact match first
    if needle in _team_cache:
        return _team_cache[needle]

    # Partial match — handles "Bayern" matching "Bayern München" etc.
    for name, tid in _team_cache.items():
        if needle in name or name in needle:
            return tid

    return None


# -----------------------------
# TEAM FORM
# -----------------------------
def get_team_form(team_id: int, limit: int = 10):
    """
    Returns {form: str, goals_for: int, goals_against: int}
    where form is a string like "WWDLW" oldest to most recent.
    Returns None if the API call fails or no completed matches found.
    """
    data = api_get(f"/teams/{team_id}/matches?limit={limit}")

    if not data:
        return None

    form          = []
    goals_for     = 0
    goals_against = 0

    for m in data.get("matches", []):
        score = m.get("score", {}).get("fullTime", {})

        # Skip unplayed / in-progress matches
        if score.get("home") is None or score.get("away") is None:
            continue

        is_home = m["homeTeam"]["id"] == team_id
        gf = score["home"] if is_home else score["away"]
        ga = score["away"] if is_home else score["home"]

        goals_for     += gf
        goals_against += ga

        if gf > ga:
            form.append("W")
        elif gf == ga:
            form.append("D")
        else:
            form.append("L")

    if not form:
        return None

    return {
        "form":          "".join(form),
        "goals_for":     goals_for,
        "goals_against": goals_against
    }