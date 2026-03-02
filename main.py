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


def download_image(url, path="temp.jpg"):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            return path
    except:
        pass
    return None


def process_item(item):

    title = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    score = item.get("score", 0)

    # -----------------------------
    # CORE ENRICHMENT
    # -----------------------------
    insight = item.get("insight")
    confidence = item.get("confidence")
    narrative = item.get("narrative", "")

    # -----------------------------
    # ANGLE + EDITORIAL
    # -----------------------------
    item["angle"] = get_angle(item)
    editorial = build_editorial_context(item)

    # -----------------------------
    # NEW LAYERS
    # -----------------------------
    personality = choose_personality(item)
    fmt = choose_format(item)

    print(f"\n--- ({score}) [{personality}] [{fmt}] ---")
    print(title)

    # -----------------------------
    # GENERATE
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
    # IMAGE
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
            except:
                pass

    # -----------------------------
    # PUSH
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


def run():

    print("=== START ===")

    news = fetch_news()
    fixtures = fetch_fixtures()

    all_content = news + fixtures

    enriched = []

    for item in all_content:
        try:
            item = enrich_item(item)
            item = compute_confidence(item)

            update_memory(item)
            item["narrative"] = get_narrative(item)

            enriched.append(item)

        except Exception as e:
            print("Enrich error:", e)
            enriched.append(item)

    ranked = rank_news(enriched)

    for item in ranked:
        process_item(item)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()