import re
import time
import requests

from fetch_news import fetch_news
from fetch_fixtures import fetch_fixtures
from generate_caption import generate_content
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new
from rank_news import rank_news, rescore_ranked
from upload_image import upload_image
from intelligence import enrich_item
from confidence_engine import compute_confidence
from narrative_memory import update_memory, get_narrative
from editorial_brain import build_editorial_context
from personality_engine import choose_personality
from format_engine import choose_format
from predictive_edge_engine import compute_edge
from daily_edge_index import generate_daily_edge_index
from team_intelligence_engine import refresh_teams
from league_intelligence import build_power_post


# --------------------------------------------------
# ENTITY DATABASE — ALL MAJOR LEAGUES + INTERNATIONAL
# --------------------------------------------------

KNOWN_TEAMS = [
    # Premier League
    "Arsenal", "Chelsea", "Liverpool", "Manchester City",
    "Manchester United", "Tottenham", "Newcastle", "Aston Villa",
    "Brighton", "West Ham",
    # La Liga
    "Real Madrid", "Barcelona", "Atletico Madrid",
    "Sevilla", "Villarreal", "Real Sociedad",
    # Bundesliga
    "Bayern Munich", "Borussia Dortmund", "RB Leipzig",
    "Bayer Leverkusen", "Eintracht Frankfurt",
    # Serie A
    "Inter", "AC Milan", "Juventus", "Napoli",
    "Roma", "Lazio", "Atalanta", "Fiorentina",
    # Ligue 1
    "PSG", "Marseille", "Lyon", "Monaco", "Lille", "Nice",
    # International
    "England", "France", "Germany", "Spain", "Italy",
    "Brazil", "Argentina", "Portugal", "Netherlands", "Belgium",
]

KNOWN_PLAYERS = [
    "Messi", "Ronaldo", "Bellingham", "Mbappe", "Haaland",
    "Saka", "De Bruyne", "Rashford", "Kane", "Vinicius",
    "Salah", "Nunez", "Martinelli", "Odegaard", "Palmer",
    "Yamal", "Olmo", "Wirtz", "Florian Wirtz",
]


# --------------------------------------------------
# TEAM → LEAGUE MAP (used in extract_entities)
# Uses word-boundary regex to avoid false positives
# --------------------------------------------------

TEAM_LEAGUE_MAP = {
    # Premier League
    "arsenal":              "Premier League",
    "chelsea":              "Premier League",
    "liverpool":            "Premier League",
    "manchester city":      "Premier League",
    "man city":             "Premier League",
    "manchester united":    "Premier League",
    "man united":           "Premier League",
    "tottenham":            "Premier League",
    "spurs":                "Premier League",
    "newcastle":            "Premier League",
    "aston villa":          "Premier League",
    "brighton":             "Premier League",
    "west ham":             "Premier League",
    # La Liga
    "real madrid":          "La Liga",
    "barcelona":            "La Liga",
    "barca":                "La Liga",
    "atletico":             "La Liga",
    "atletico madrid":      "La Liga",
    "sevilla":              "La Liga",
    "villarreal":           "La Liga",
    # Bundesliga
    "bayern":               "Bundesliga",
    "bayern munich":        "Bundesliga",
    "dortmund":             "Bundesliga",
    "borussia dortmund":    "Bundesliga",
    "rb leipzig":           "Bundesliga",
    "leverkusen":           "Bundesliga",
    "bayer leverkusen":     "Bundesliga",
    # Serie A
    "inter":                "Serie A",
    "inter milan":          "Serie A",
    "ac milan":             "Serie A",
    "milan":                "Serie A",
    "juventus":             "Serie A",
    "napoli":               "Serie A",
    "roma":                 "Serie A",
    "lazio":                "Serie A",
    "atalanta":             "Serie A",
    # Ligue 1
    "psg":                  "Ligue 1",
    "paris saint-germain":  "Ligue 1",
    "paris saint germain":  "Ligue 1",
    "marseille":            "Ligue 1",
    "lyon":                 "Ligue 1",
    "monaco":               "Ligue 1",
    "lille":                "Ligue 1",
    # International
    "england":              "International",
    "france":               "International",
    "germany":              "International",
    "spain":                "International",
    "brazil":               "International",
    "argentina":            "International",
    "portugal":             "International",
    "italy":                "International",
    "netherlands":          "International",
    "belgium":              "International",
}

COMPETITION_LEAGUE_MAP = {
    "premier league":   "Premier League",
    "la liga":          "La Liga",
    "bundesliga":       "Bundesliga",
    "serie a":          "Serie A",
    "ligue 1":          "Ligue 1",
    "champions league": "Champions League",
    "europa league":    "Europa League",
    "world cup":        "International",
    "euros":            "International",
    "nations league":   "International",
}


# --------------------------------------------------
# ENTITY EXTRACTION — uses word boundaries
# --------------------------------------------------

def extract_entities(title: str):
    """
    Extracts league, team, and player from a title.
    Uses \b word boundaries to avoid false positives
    e.g. 'Inter' matching 'interesting', 'City' matching 'Ivory Coast'.
    """
    title_lower = title.lower()

    league      = ""
    team_found  = ""
    player_found = ""

    # Team detection — longest match first to prefer "manchester city" over "city"
    sorted_teams = sorted(TEAM_LEAGUE_MAP.keys(), key=len, reverse=True)
    for team in sorted_teams:
        pattern = r'\b' + re.escape(team) + r'\b'
        if re.search(pattern, title_lower):
            team_found = team.title()
            league     = TEAM_LEAGUE_MAP[team]
            break

    # Competition detection (if no team found a league yet)
    if not league:
        for comp, lg in COMPETITION_LEAGUE_MAP.items():
            if comp in title_lower:
                league = lg
                break

    # Player detection
    for p in KNOWN_PLAYERS:
        if p.lower() in title_lower:
            player_found = p
            break

    return league, team_found, player_found


# --------------------------------------------------
# IMAGE DOWNLOAD
# --------------------------------------------------

def download_image(url, path="temp.jpg"):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            return path
    except Exception as e:
        print("Download error:", e)
    return None


# --------------------------------------------------
# PROCESS ITEM
# --------------------------------------------------

def process_item(item):

    title   = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    score   = item.get("score", 0)

    print(f"\n--- ({score}) ---")
    print(title)

    # --------------------------------
    # ENRICH
    # --------------------------------
    try:
        item = enrich_item(item)
        item = compute_confidence(item)
        update_memory(item)
        item["narrative"] = get_narrative(item)
    except Exception as e:
        print("Enrich error:", e)

    insight    = item.get("insight")
    confidence = item.get("confidence")
    narrative  = item.get("narrative", "")

    # --------------------------------
    # ENTITY EXTRACTION
    # --------------------------------
    league = item.get("league", "")
    teams  = item.get("teams", [])
    player = item.get("player", "")

    if not league or not teams:
        league_guess, team_guess, player_guess = extract_entities(title)
        if league_guess and not league:
            league = league_guess
        if team_guess and not teams:
            teams = [team_guess]
        if player_guess and not player:
            player = player_guess

    team_string = ", ".join(teams) if isinstance(teams, list) else (teams or "")

    # --------------------------------
    # EDGE MODEL
    # --------------------------------
    if teams and len(teams) == 2:
        try:
            item["edge"] = compute_edge(teams[0], teams[1], confidence)
        except Exception as e:
            print("Edge error:", e)

    # --------------------------------
    # EDITORIAL
    # --------------------------------
    try:
        editorial = build_editorial_context(item)
    except Exception:
        editorial = {}

    personality = choose_personality(item)
    fmt         = choose_format(item)

    # --------------------------------
    # CONTENT GENERATION
    # --------------------------------
    overlay, short, long_cap, article = generate_content(
        title, summary, "football", context,
        insight, editorial, confidence, narrative,
        personality, fmt, item.get("edge")
    )

    # --------------------------------
    # IMAGE
    # --------------------------------
    image_url    = get_image(item)
    instagram_url = image_url
    article_url  = image_url

    if image_url:
        local = download_image(image_url)
        if local:
            try:
                create_post(local, title, overlay, "post.jpg", brand=True)
                instagram_url = upload_image("post.jpg")
            except Exception as e:
                print("Image error:", e)

    context_string = f"{context} | {personality} | {fmt}"
    ts = int(time.time())

    # --------------------------------
    # PUSH TO SHEET — INSTAGRAM ROW
    # --------------------------------
    push_if_new({
        "Type":          "instagram",
        "League":        league,
        "Team":          team_string,
        "Player":        player,
        "Category":      "football",
        "Title":         title,
        "Short Caption": short,
        "Long Caption":  long_cap,
        "Article":       "",
        "Image URL":     instagram_url,
        "Status":        "PENDING",
        "Context":       context_string,
        "Score":         score,
        "Date":          ts,
    })

    # --------------------------------
    # PUSH TO SHEET — ARTICLE ROW
    # --------------------------------
    push_if_new({
        "Type":          "article",
        "League":        league,
        "Team":          team_string,
        "Player":        player,
        "Category":      "football",
        "Title":         title,
        "Short Caption": short,
        "Long Caption":  long_cap,
        "Article":       article,
        "Image URL":     article_url,
        "Status":        "PENDING",
        "Context":       context_string,
        "Score":         score,
        "Date":          ts,
    })

    print("✓ Done")


# --------------------------------------------------
# RUN PIPELINE
# --------------------------------------------------

def run():

    print("=== GAMETRAIT SPORTSAGENT — START ===")

    # Refresh team store from football API
    try:
        refresh_teams()
    except Exception as e:
        print("Team refresh failed:", e)

    # ----------------------------------------
    # EDGE VOLATILITY INDEX
    # ----------------------------------------
    try:
        overlay, visual, caption, article = generate_daily_edge_index()
        if visual:
            create_post(
                None,
                "EDGE VOLATILITY INDEX — Gametrait™",
                visual,
                "evi_post.jpg",
                brand=True
            )
            image_url = upload_image("evi_post.jpg")
            push_if_new({
                "Type":          "instagram",
                "League":        "",
                "Team":          "",
                "Player":        "",
                "Category":      "football",
                "Title":         "EDGE VOLATILITY INDEX — Gametrait™",
                "Short Caption": overlay,
                "Long Caption":  caption,
                "Article":       article,
                "Image URL":     image_url,
                "Status":        "PENDING",
                "Context":       "daily_feature | analyst | breakdown",
                "Score":         99,
                "Date":          int(time.time()),
            })
    except Exception as e:
        print("Edge index error:", e)

    # ----------------------------------------
    # GLOBAL FORM INDEX
    # ----------------------------------------
    try:
        overlay, text = build_power_post()
        if text:
            push_if_new({
                "Type":          "instagram",
                "League":        "",
                "Team":          "",
                "Player":        "",
                "Category":      "football",
                "Title":         "Global Football Form Index",
                "Short Caption": overlay,
                "Long Caption":  text,
                "Article":       "",
                "Image URL":     "",
                "Status":        "PENDING",
                "Context":       "data_intelligence | analyst | breakdown",
                "Score":         90,
                "Date":          int(time.time()),
            })
    except Exception as e:
        print("Form index error:", e)

    # ----------------------------------------
    # NEWS + FIXTURES
    # ----------------------------------------
    news     = fetch_news()
    fixtures = fetch_fixtures()

    enriched_fixtures = []
    for f in fixtures:
        try:
            enriched_fixtures.append(enrich_item(f))
        except Exception:
            enriched_fixtures.append(f)

    all_content = news + enriched_fixtures
    ranked      = rank_news(all_content)
    ranked      = rescore_ranked(ranked)

    print(f"Total ranked items: {len(ranked)}")

    for item in ranked:
        try:
            process_item(item)
        except Exception as e:
            print("PROCESS ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()