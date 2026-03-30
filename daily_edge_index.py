import json
import os
from datetime import datetime
from football_api import api_get, get_team_id
from store import load_store, save_store


HISTORY_PATH = "evi_history.json"


# --------------------------------------------------
# ALL MAJOR LEAGUE CLUBS TO TRACK
# --------------------------------------------------

CORE_TEAMS = [
    # Premier League
    "Arsenal", "Chelsea", "Liverpool", "Manchester City",
    "Manchester United", "Tottenham", "Newcastle", "Aston Villa",

    # La Liga
    "Real Madrid", "Barcelona", "Atletico Madrid",

    # Bundesliga
    "Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen",

    # Serie A
    "Inter", "AC Milan", "Juventus", "Napoli", "Atalanta",

    # Ligue 1
    "PSG", "Marseille", "Monaco",
]


# --------------------------------------------------
# HISTORY STORE
# --------------------------------------------------

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


# --------------------------------------------------
# TEAM DATA FETCH
# --------------------------------------------------

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

    return {"recent_form": form, "goals_for": gf, "goals_against": ga}


# --------------------------------------------------
# EVI COMPONENT SCORES
# --------------------------------------------------

def momentum_score(form: list) -> float:
    """
    Weighted form over last 5 games — most recent match counts most.
    W = +3 pts, D = +1, L = -2, with recency multiplier.
    """
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
    """
    Goal difference as a proxy for dominance.
    Positive = scoring more than conceding.
    """
    return (team.get("goals_for", 0) - team.get("goals_against", 0)) * 0.5


def instability_score(form: list) -> float:
    """
    Counts result swings (W→L, L→W, W→D etc).
    Higher = more volatile / unpredictable.
    This SUBTRACTS from EVI — instability is bad.
    """
    swings = sum(1 for i in range(1, len(form)) if form[i] != form[i - 1])
    return swings * 1.2


def compute_evi(team: dict) -> float | None:
    """
    EVI = weighted sum of momentum + control - instability.
    Normalised to a 0–10 scale.

    Instability SUBTRACTS — a volatile team should score lower
    even if it has some wins. Previously this was being added
    which caused volatile/inconsistent clubs to score too high.
    """
    form = team.get("recent_form", [])
    if len(form) < 5:
        return None

    raw = (
        momentum_score(form)    * 0.50
        + control_score(team)   * 0.35
        - instability_score(form) * 0.15    # SUBTRACT — instability is bad
    )

    # Normalise to 0–10. Raw range roughly -30 to +50.
    normalised = (raw + 30) / 8
    return round(max(0.0, min(10.0, normalised)), 1)


# --------------------------------------------------
# HUMAN-READABLE OUTPUT HELPERS
# --------------------------------------------------

def evi_band(score: float) -> str:
    """Colour band for EVI score."""
    if score >= 7.0: return "🔴"   # Surging — strong momentum
    if score >= 4.5: return "🟡"   # Stable — consistent
    return "🟢"                    # Caution — volatile or poor form


def delta_arrow(team: str, score: float, prev: dict) -> str:
    """Shows change vs previous day's EVI."""
    if team not in prev:
        return ""
    d = score - prev[team]
    if d > 0.3:  return f"↑ +{d:.1f}"
    if d < -0.3: return f"↓ {d:.1f}"
    return f"→ {d:+.1f}"


def evi_narrative(team: str, score: float, form: list) -> str:
    """One-line pundit-style read of the team's current state."""
    wins   = form.count("W")
    losses = form.count("L")
    draws  = form.count("D")

    if score >= 7.0:
        if wins >= 4:
            return f"{wins}W in last 5 — dominant form, momentum fully behind them."
        return f"Strong surge — {wins}W, {draws}D. Control metrics leading the index."
    if score >= 4.5:
        if losses == 0:
            return f"Unbeaten run intact — {wins}W, {draws}D. Solid but not spectacular."
        return f"Consistent enough — {wins}W but {losses}L introduces a note of caution."
    if losses >= 3:
        return f"Alarm bells — {losses}L in last 5. Form collapse, table may not yet show it."
    return f"Volatility warning — {losses}L in recent run. Unpredictable phase."


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def generate_daily_edge_index():

    store   = load_store()
    history = load_history()

    # Fetch any CORE_TEAMS missing from store
    for team in CORE_TEAMS:
        if team not in store:
            print(f"Fetching missing team: {team}")
            data = fetch_team_data(team)
            if data:
                store[team] = data
    save_store(store)

    # Compute EVI for all teams in store
    scores = [
        (team, evi)
        for team, data in store.items()
        if (evi := compute_evi(data)) is not None
    ]

    if not scores:
        return None, None, None, None

    scores.sort(key=lambda x: x[1], reverse=True)
    top5 = scores[:5]

    # Build previous-day lookup for deltas
    all_dates = [k for k in history if k != "latest" and k != datetime.utcnow().strftime("%Y-%m-%d")]
    prev_raw  = history.get(sorted(all_dates)[-1], []) if all_dates else []
    prev      = {t: s for t, s in prev_raw} if prev_raw else {}

    # --------------------------------------------------
    # INSTAGRAM CARD TEXT (visual_text)
    # e.g. "🔴 Arsenal  EVI 8.4  ↑ +1.2"
    # --------------------------------------------------
    card_lines = []
    for team, score in top5:
        arrow = delta_arrow(team, score, prev)
        card_lines.append(f"{evi_band(score)} {team}  EVI {score}  {arrow}".strip())
    visual_text = "\n".join(card_lines)

    # --------------------------------------------------
    # FULL CAPTION (for Google Sheet / article)
    # Human-readable with narrative per team
    # --------------------------------------------------
    date_str = datetime.utcnow().strftime("%A %d %B %Y")

    cap_lines = [
        "GAMETRAIT EDGE VOLATILITY INDEX",
        f"Daily Intelligence · {date_str}",
        "",
    ]

    for team, score in top5:
        form      = store.get(team, {}).get("recent_form", [])
        arrow     = delta_arrow(team, score, prev)
        narrative = evi_narrative(team, score, form)
        line      = f"{evi_band(score)} {team}  EVI {score}  {arrow}".strip()
        cap_lines.append(line)
        cap_lines.append(f'   "{narrative}"')
        cap_lines.append("")

    cap_lines.append(
        "EVI measures momentum, control and instability across elite clubs. "
        "Higher score = stronger competitive position right now."
    )

    caption = "\n".join(cap_lines)

    # --------------------------------------------------
    # ARTICLE
    # --------------------------------------------------
    leader       = top5[0][0]
    leader_score = top5[0][1]
    leader_form  = store.get(leader, {}).get("recent_form", [])
    leader_wins  = leader_form.count("W")

    article = (
        f"The Gametrait Edge Volatility Index tracks which clubs hold "
        f"the strongest competitive momentum across elite European football.\n\n"
        f"Unlike traditional league tables, the EVI blends recent form weighting, "
        f"goal control differentials and volatility patterns to detect where "
        f"pressure and momentum are genuinely building — often before it shows "
        f"in the standings.\n\n"
        f"Today's leader is {leader} with an EVI of {leader_score}. "
        f"With {leader_wins} wins in their last five matches, their combination "
        f"of consistent results and strong goal control places them at the top "
        f"of the index.\n\n"
    )

    if len(top5) > 1:
        bottom      = top5[-1]
        bottom_form = store.get(bottom[0], {}).get("recent_form", [])
        bottom_loss = bottom_form.count("L")
        article += (
            f"At the other end of today's index, {bottom[0]} scores {bottom[1]} — "
            f"with {bottom_loss} losses in recent outings, the volatility model "
            f"flags them as entering an unpredictable phase that the table "
            f"may not yet fully reflect.\n\n"
        )

    article += (
        f"By measuring volatility rather than simply results, the EVI often "
        f"surfaces shifts in competitive power before they appear in league tables. "
        f"Follow Gametrait daily for the full picture."
    )

    # --------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------
    today = datetime.utcnow().strftime("%Y-%m-%d")
    history["latest"]  = top5
    history[today]     = top5
    save_history(history)

    return "EDGE VOLATILITY INDEX", visual_text, caption, article