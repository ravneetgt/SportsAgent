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
# ENTITY DATABASE (FIXED — GLOBAL COVERAGE)
# --------------------------------------------------

KNOWN_TEAMS = [
    # England
    "Arsenal","Chelsea","Liverpool","Manchester City","Manchester United",
    "Tottenham","Newcastle",

    # Spain
    "Real Madrid","Barcelona","Atletico Madrid",

    # Germany
    "Bayern Munich","Borussia Dortmund","RB Leipzig",

    # Italy
    "Inter","AC Milan","Juventus","Napoli","Roma",

    # France
    "PSG","Marseille","Lyon"
]

KNOWN_PLAYERS = [
    "Messi","Ronaldo","Bellingham","Mbappe","Haaland",
    "Saka","De Bruyne","Rashford","Kane"
]


# --------------------------------------------------
# ENTITY EXTRACTION (FIXED — NO EPL BIAS)
# --------------------------------------------------

def extract_entities(title):

    title_lower = title.lower()

    TEAM_LEAGUE_MAP = {
        # England
        "arsenal": "Premier League",
        "chelsea": "Premier League",
        "liverpool": "Premier League",
        "manchester city": "Premier League",
        "manchester united": "Premier League",
        "tottenham": "Premier League",
        "newcastle": "Premier League",

        # Spain
        "real madrid": "La Liga",
        "barcelona": "La Liga",
        "atletico": "La Liga",

        # Germany
        "bayern": "Bundesliga",
        "dortmund": "Bundesliga",
        "leipzig": "Bundesliga",

        # Italy
        "inter": "Serie A",
        "milan": "Serie A",
        "juventus": "Serie A",
        "napoli": "Serie A",
        "roma": "Serie A",

        # France
        "psg": "Ligue 1",
        "marseille": "Ligue 1",
        "lyon": "Ligue 1"
    }

    league = ""
    team_found = ""
    player_found = ""

    for team, lg in TEAM_LEAGUE_MAP.items():
        if team in title_lower:
            team_found = team.title()
            league = lg
            break

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

    if not league and not teams:

        league_guess, team_guess, player_guess = extract_entities(title)

        if league_guess:
            league = league_guess

        if team_guess:
            teams = [team_guess]

        if player_guess and not player:
            player = player_guess

    if isinstance(teams, list):
        team_string = ", ".join(teams)
    else:
        team_string = teams or ""

    # --------------------------------
    # EDGE MODEL
    # --------------------------------

    if teams and len(teams) == 2:

        try:
            item["edge"] = compute_edge(
                teams[0],
                teams[1],
                confidence
            )

        except Exception as e:
            print("Edge error:", e)

    # --------------------------------
    # EDITORIAL
    # --------------------------------

    try:
        editorial = build_editorial_context(item)
    except:
        editorial = {}

    personality = choose_personality(item)
    fmt         = choose_format(item)

    # --------------------------------
    # CONTENT
    # --------------------------------

    overlay, short, long_cap, article = generate_content(
        title,
        summary,
        "football",
        context,
        insight,
        editorial,
        confidence,
        narrative,
        personality,
        fmt,
        item.get("edge")
    )

    # --------------------------------
    # IMAGE
    # --------------------------------

    image_url = get_image(item)

    instagram_url = image_url
    article_url   = image_url

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
    # INSTAGRAM ROW
    # --------------------------------

    push_if_new({
        "Type": "instagram",
        "League": league,
        "Team": team_string,
        "Player": player,
        "Category": "football",
        "Title": title,
        "Short Caption": short,
        "Long Caption": long_cap,
        "Article": "",
        "Image URL": instagram_url,
        "Status": "PENDING",
        "Context": context_string,
        "Score": score,
        "Date": ts
    })

    # --------------------------------
    # ARTICLE ROW
    # --------------------------------

    push_if_new({
        "Type": "article",
        "League": league,
        "Team": team_string,
        "Player": player,
        "Category": "football",
        "Title": title,
        "Short Caption": short,
        "Long Caption": long_cap,
        "Article": article,
        "Image URL": article_url,
        "Status": "PENDING",
        "Context": context_string,
        "Score": score,
        "Date": ts
    })

    print("✓ Done")


# --------------------------------------------------
# RUN PIPELINE
# --------------------------------------------------

def run():

    print("=== START ===")

    try:
        refresh_teams()
    except Exception as e:
        print("Team refresh failed:", e)

    # EDGE INDEX
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
                "Type": "instagram",
                "League": "",
                "Team": "",
                "Player": "",
                "Category": "football",
                "Title": "EDGE VOLATILITY INDEX — Gametrait™",
                "Short Caption": overlay,
                "Long Caption": caption,
                "Article": article,
                "Image URL": image_url,
                "Status": "PENDING",
                "Context": "daily_feature | analyst | breakdown",
                "Score": 99,
                "Date": int(time.time())
            })

    except Exception as e:
        print("Edge index error:", e)

    # FORM INDEX
    try:

        overlay, text = build_power_post()

        if text:

            push_if_new({
                "Type": "instagram",
                "League": "",
                "Team": "",
                "Player": "",
                "Category": "football",
                "Title": "Global Football Form Index",
                "Short Caption": overlay,
                "Long Caption": text,
                "Article": "",
                "Image URL": "",
                "Status": "PENDING",
                "Context": "data_intelligence | analyst | breakdown",
                "Score": 90,
                "Date": int(time.time())
            })

    except Exception as e:
        print("Form index error:", e)

    # NEWS + FIXTURES
    news     = fetch_news()
    fixtures = fetch_fixtures()

    enriched_fixtures = []

    for f in fixtures:
        try:
            enriched_fixtures.append(enrich_item(f))
        except:
            enriched_fixtures.append(f)

    all_content = news + enriched_fixtures

    ranked = rank_news(all_content)
    ranked = rescore_ranked(ranked)

    print("Total ranked items:", len(ranked))

    for item in ranked:
        try:
            process_item(item)
        except Exception as e:
            print("PROCESS ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()