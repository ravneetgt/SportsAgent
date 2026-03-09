import time
import requests

from fetch_news import fetch_news
from fetch_fixtures import fetch_fixtures
from generate_caption import generate_content
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new
from rank_news import rank_news

from intelligence import enrich_item
from confidence_engine import compute_confidence
from narrative_memory import update_memory, get_narrative
from angle_engine import get_angle
from editorial_brain import build_editorial_context
from personality_engine import choose_personality
from format_engine import choose_format

from daily_edge_index import generate_daily_edge_index


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
# PROCESS CONTENT ITEM
# --------------------------------------------------

def process_item(item):

    title = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    score = item.get("score", 0)

    print(f"\n--- ({score}) ---")
    print(title)

    # -----------------------------
    # ENRICHMENT + MEMORY
    # -----------------------------
    try:
        item = enrich_item(item)
        item = compute_confidence(item)

        update_memory(item)
        item["narrative"] = get_narrative(item)

    except Exception as e:
        print("Enrich error:", e)

    insight = item.get("insight")
    confidence = item.get("confidence")
    narrative = item.get("narrative", "")

    # -----------------------------
    # EDITORIAL
    # -----------------------------
    try:
        item["angle"] = get_angle(item)
        editorial = build_editorial_context(item)
    except:
        editorial = {}

    personality = choose_personality(item)
    fmt = choose_format(item)

    print(f"[{personality}] [{fmt}]")

    # -----------------------------
    # AI GENERATION
    # -----------------------------
    overlay, short, long, article = generate_content(
        title,
        summary,
        "football",
        context,
        insight,
        editorial,
        confidence,
        narrative,
        personality,
        fmt
    )

    # -----------------------------
    # IMAGE PROCESSING
    # -----------------------------
    image_url = get_image(item)
    final_url = image_url

    if image_url:
        local = download_image(image_url)

        if local:
            try:
                create_post(local, title, overlay, "post.jpg")
                from upload_image import upload_image
                final_url = upload_image("post.jpg")
            except Exception as e:
                print("Image error:", e)

    # -----------------------------
    # PUSH INSTAGRAM (NO edge_text here)
    # -----------------------------
    push_if_new({
        "Type": "instagram",
        "Category": "football",
        "Title": title,
        "Short Caption": short,
        "Long Caption": long,
        "Article": "",
        "Image URL": final_url,
        "Status": "PENDING",
        "Context": context,
        "Score": score,
        "Date": int(time.time())
    })

    # -----------------------------
    # PUSH ARTICLE
    # -----------------------------
    push_if_new({
        "Type": "article",
        "Category": "football",
        "Title": title,
        "Short Caption": short,
        "Long Caption": long,
        "Article": article,
        "Image URL": final_url,
        "Status": "PENDING",
        "Context": context,
        "Score": score,
        "Date": int(time.time())
    })

    print("✓ Done")


# --------------------------------------------------
# MAIN RUNNER
# --------------------------------------------------

def run():

    print("=== START ===")

    # --------------------------------------------------
    # DAILY GAMETRAIT EVI™ FEATURE
    # --------------------------------------------------

    overlay, edge_text = generate_daily_edge_index()

    if edge_text:
        push_if_new({
            "Type": "instagram",
            "Category": "football",
            "Title": "GAMETRAIT EVI™ — Daily Ranking",
            "Short Caption": "Edge Volatility Index",
            "Long Caption": edge_text,
            "Article": "",
            "Image URL": "",
            "Status": "PENDING",
            "Context": "daily_feature",
            "Score": 99,
            "Date": int(time.time())
        })

    # --------------------------------------------------
    # FETCH CONTENT
    # --------------------------------------------------

    news = fetch_news()
    fixtures = fetch_fixtures()

    all_content = news + fixtures

    ranked = rank_news(all_content)

    for item in ranked:
        try:
            process_item(item)
        except Exception as e:
            print("PROCESS ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()