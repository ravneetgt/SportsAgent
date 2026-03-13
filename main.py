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

    title = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    score = item.get("score", 0)

    print(f"\n--- ({score}) ---")
    print(title)

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

    teams = item.get("teams")

    if teams and len(teams) == 2:

        edge = compute_edge(
            teams[0],
            teams[1],
            confidence
        )

        item["edge"] = edge

    try:
        editorial = build_editorial_context(item)
    except:
        editorial = {}

    personality = choose_personality(item)
    fmt = choose_format(item)

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
        fmt,
        item.get("edge")
    )

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

    context_string = f"{context} | {personality} | {fmt}"

    push_if_new({
        "Type": "instagram",
        "Category": "football",
        "Title": title,
        "Short Caption": short,
        "Long Caption": long,
        "Article": "",
        "Image URL": final_url,
        "Status": "PENDING",
        "Context": context_string,
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
        "Context": context_string,
        "Score": score,
        "Date": int(time.time())
    })

    print("✓ Done")


def run():

    print("=== START ===")

    try:
        refresh_teams()
    except Exception as e:
        print("Team intelligence refresh failed:", e)

    # -------- DAILY EDGE INDEX --------

    try:

        overlay, visual, caption, article = generate_daily_edge_index()

        if visual:

            create_post(
                None,
                "EDGE VOLATILITY INDEX",
                visual,
                "evi_post.jpg"
            )

            from upload_image import upload_image

            image_url = upload_image("evi_post.jpg")

            push_if_new({
                "Type": "instagram",
                "Category": "football",
                "Title": "GAMETRAIT — Daily Edge Intelligence",
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

    # -------- GLOBAL FORM INDEX --------

    try:

        overlay, text = build_power_post()

        if text:

            push_if_new({
                "Type": "instagram",
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

    news = fetch_news()
    fixtures = fetch_fixtures()

    all_content = news + fixtures

    ranked = rank_news(all_content)

    print("Total ranked items:", len(ranked))

    for item in ranked:

        try:
            process_item(item)
        except Exception as e:
            print("PROCESS ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":

    run()