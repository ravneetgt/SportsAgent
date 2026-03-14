from datetime import datetime
from football_api import api_get, get_team_id
from store import load_store, save_store


def update_team(team_id: int, team_name: str) -> dict | None:
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

        is_home     = m["homeTeam"]["id"] == team_id
        goals_for   = score["home"] if is_home else score["away"]
        goals_against = score["away"] if is_home else score["home"]

        gf += goals_for
        ga += goals_against

        if goals_for > goals_against:
            form.append("W")
        elif goals_for == goals_against:
            form.append("D")
        else:
            form.append("L")

    if not form:
        return None

    return {
        "recent_form":   form,
        "goals_for":     gf,
        "goals_against": ga,
        "mention_count": 0,
        "last_seen":     str(datetime.utcnow()),
        "last_insight_hash": None
    }


def refresh_teams():
    """
    Fetches up to 40 teams from the API and writes fresh match data
    to memory_store.json. Only overwrites form/goal fields — preserves
    mention_count and last_insight_hash set by narrative_memory.
    Uses /teams (free tier). /competitions/{comp}/teams requires paid plan.
    """
    store = load_store()

    data = api_get("/teams")
    if not data:
        print("refresh_teams: could not fetch team list")
        return

    for team in data.get("teams", [])[:40]:
        name = team["name"]
        tid  = team["id"]

        print("Updating", name)

        updated = update_team(tid, name)
        if not updated:
            continue

        existing = store.get(name, {})

        # Merge: keep narrative_memory fields, overwrite match data
        existing.update(updated)
        store[name] = existing

    save_store(store)