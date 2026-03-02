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


# -----------------------------
# DOWNLOAD IMAGE
# -----------------------------
def download_image(url, path="temp.jpg"):
    try:
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            return path

        print("Image download failed:", res.status_code)

    except Exception as e:
        print("Download error:", e)

    return None


# -----------------------------
# PROCESS ITEM
# -----------------------------
def process_item(item):

    title = item.get("title", "")
    summary = item.get("summary", "")
    context = item.get("context", "news")
    insight = item.get("insight")
    score = item.get("score", 0)

    print(f"\n--- Processing ({score}) ---")
    print(title)

    # -----------------------------
    # AI CONTENT
    # -----------------------------
    result = generate_content(
        title,
        summary,
        "football",
        context,
        insight
    )

    if not result or len(result) != 4:
        print("Fallback triggered")
        overlay, short, long, article = title[:80], title, summary, summary
    else:
        overlay, short, long, article = result

    # -----------------------------
    # IMAGE (IMPORTANT FIX)
    # -----------------------------
    image_url = get_image(item)   # FIXED
    final_url = image_url

    if image_url:
        local = download_image(image_url)

        if local:
            try:
                final_path = "post.jpg"

                create_post(
                    local,
                    title,
                    overlay,
                    final_path
                )

                # -----------------------------
                # UPLOAD
                # -----------------------------
                try:
                    from upload_image import upload_image

                    final_url = upload_image(final_path)
                    print("Uploaded:", final_url)

                except Exception as e:
                    print("Upload skipped:", e)

            except Exception as e:
                print("Post creation error:", e)

    # -----------------------------
    # INSTAGRAM
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
    # ARTICLE
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


# -----------------------------
# MAIN
# -----------------------------
def run():

    print("=== START ===")

    news = fetch_news()
    fixtures = fetch_fixtures()

    print("NEWS:", len(news))
    print("FIXTURES:", len(fixtures))

    all_content = news + fixtures

    if not all_content:
        print("No content found")
        return

    # -----------------------------
    # INTELLIGENCE
    # -----------------------------
    enriched = []

    for item in all_content:
        try:
            enriched.append(enrich_item(item))
        except Exception as e:
            print("Intelligence error:", e)
            enriched.append(item)

    # -----------------------------
    # RANKING
    # -----------------------------
    ranked = rank_news(enriched)

    print("SELECTED:", len(ranked))

    if not ranked:
        print("No ranked content")
        return

    # -----------------------------
    # PROCESS
    # -----------------------------
    for item in ranked:

        try:
            process_item(item)
        except Exception as e:
            print("ERROR:", e)

    print("=== COMPLETE ===")


if __name__ == "__main__":
    run()