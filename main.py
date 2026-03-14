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


def process_item(item):

    title   = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    score   = item.get("score", 0)

    print(f"\n--- ({score}) ---")
    print(title)

    # --------------------------------------------------
    # ENRICH + MEMORY
    # enrich_item only does API work for preview fixtures,
    # so news items pass through cheaply.
    # --------------------------------------------------
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

    # --------------------------------------------------
    # EDGE MODEL
    # --------------------------------------------------
    teams = item.get("teams")
    if teams and len(teams) == 2:
        try:
            item["edge"] = compute_edge(teams[0], teams[1], confidence)
        except Exception as e:
            print("Edge error:", e)
            item["edge"] = None

    # --------------------------------------------------
    # EDITORIAL CONTEXT
    # --------------------------------------------------
    try:
        editorial = build_editorial_context(item)
    except Exception as e:
        print("Editorial error:", e)
        editorial = {}

    personality = choose_personality(item)
    fmt         = choose_format(item)

    # --------------------------------------------------
    # CAPTION GENERATION
    # --------------------------------------------------
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

    # --------------------------------------------------
    # IMAGE — fetch, render post card, upload
    # --------------------------------------------------
    image_url = get_image(item)
    final_url = image_url  # fallback: raw Pexels URL

    if image_url:
        local = download_image(image_url)
        if local:
            try:
                create_post(local, title, overlay, "post.jpg")
                final_url = upload_image("post.jpg")
            except Exception as e:
                print("Image upload error:", e)

    # --------------------------------------------------
    # PUSH TO SHEET
    # --------------------------------------------------
    context_string = f"{context} | {personality} | {fmt}"
    ts = int(time.time())

    push_if_new({
        "Type":          "instagram",
        "Category":      "football",
        "Title":         title,
        "Short Caption": short,
        "Long Caption":  long_cap,
        "Article":       "",
        "Image URL":     final_url,
        "Status":        "PENDING",
        "Context":       context_string,
        "Score":         score,
        "Date":          ts
    })

    push_if_new({
        "Type":          "article",
        "Category":      "football",
        "Title":         title,
        "Short Caption": short,
        "Long Caption":  long_cap,
        "Article":       article,
        "Image URL":     final_url,
        "Status":        "PENDING",
        "Context":       context_string,
        "Score":         score,
        "Date":          ts
    })

    print("✓ Done")


def run():

    print("=== START ===")

    # --------------------------------------------------
    # TEAM INTELLIGENCE REFRESH
    # Populates memory_store.json with fresh API match data.
    # Runs first so downstream modules have current form.
    # --------------------------------------------------
    try:
        refresh_teams()
    except Exception as e:
        print("Team intelligence refresh failed:", e)

    # --------------------------------------------------
    # DAILY EDGE INDEX
    # Standalone feature post — not part of news pipeline.
    # --------------------------------------------------
    try:
        overlay, visual, caption, article = generate_daily_edge_index()

        if visual:
            create_post(None, "EDGE VOLATILITY INDEX", visual, "evi_post.jpg")
            image_url = upload_image("evi_post.jpg")

            push_if_new({
                "Type":          "instagram",
                "Category":      "football",
                "Title":         "GAMETRAIT — Daily Edge Intelligence",
                "Short Caption": overlay,
                "Long Caption":  caption,
                "Article":       article,
                "Image URL":     image_url,
                "Status":        "PENDING",
                "Context":       "daily_feature | analyst | breakdown",
                "Score":         99,
                "Date":          int(time.time())
            })

    except Exception as e:
        print("Edge index error:", e)

    # --------------------------------------------------
    # GLOBAL FORM INDEX
    # --------------------------------------------------
    try:
        overlay, text = build_power_post()

        if text:
            push_if_new({
                "Type":          "instagram",
                "Category":      "football",
                "Title":         "Global Football Form Index",
                "Short Caption": overlay,
                "Long Caption":  text,
                "Article":       "",
                "Image URL":     "",
                "Status":        "PENDING",
                "Context":       "data_intelligence | analyst | breakdown",
                "Score":         90,
                "Date":          int(time.time())
            })

    except Exception as e:
        print("Form index error:", e)

    # --------------------------------------------------
    # NEWS PIPELINE
    #
    # Order matters:
    #   1. Fetch news + fixtures
    #   2. Enrich fixtures BEFORE ranking so insight scores fire
    #   3. Base rank (recency, clubs, intent)
    #   4. Re-score with insight boosts now that data exists
    #   5. Process each item (enrich_item is idempotent — fixtures
    #      already enriched here just return early)
    # --------------------------------------------------
    news     = fetch_news()
    fixtures = fetch_fixtures()

    # Pre-enrich fixtures so rank_news can see insight data
    enriched_fixtures = []
    for f in fixtures:
        try:
            enriched_fixtures.append(enrich_item(f))
        except Exception as e:
            print("Pre-enrich error:", e)
            enriched_fixtures.append(f)

    all_content = news + enriched_fixtures

    ranked = rank_news(all_content)        # base score
    ranked = rescore_ranked(ranked)        # add insight boost

    print("Total ranked items:", len(ranked))

    for item in ranked:
        try:
            process_item(item)
        except Exception as e:
            print("PROCESS ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()
