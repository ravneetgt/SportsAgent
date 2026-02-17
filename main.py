from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image
from push_to_sheet import push_if_new
from create_post import create_post


def run():
    print("\nRUNNING MAIN...\n")

    news = fetch_news()

    if not news:
        print("No news found.")
        return

    print("Total articles fetched:", len(news))

    added_count = 0
    skipped_count = 0

    for i, article in enumerate(news):
        print("\n========================")
        print(f"Processing {i+1}/{len(news)}")

        title = article.get("title", "")
        summary = article.get("summary", "")
        category = article.get("category", "")
        query = article.get("query", "")

        print("CATEGORY:", category)
        print("TITLE:", title)

        try:
            # -----------------------------
            # 1. Generate caption
            # -----------------------------
            caption = generate_caption(title, summary, category)

            print("\nCAPTION:")
            print(caption)

            # -----------------------------
            # 2. Fetch image
            # -----------------------------
            image_url = get_image(title, category)

            print("\nRAW IMAGE URL:", image_url)

            if not image_url:
                print("Skipping - no image")
                skipped_count += 1
                continue

            # -----------------------------
            # 3. Create branded image
            # -----------------------------
            final_image_path = create_post(image_url, title, caption)

            print("FINAL IMAGE:", final_image_path)

            if not final_image_path:
                print("Skipping - image generation failed")
                skipped_count += 1
                continue

            # -----------------------------
            # 4. Save to Google Sheet
            # -----------------------------
            added = push_if_new(article, caption, final_image_path)

            if added:
                added_count += 1
                print("✔ ADDED")
            else:
                skipped_count += 1
                print("⚠ SKIPPED")

        except Exception as e:
            print("❌ ERROR:", e)

    print("\n========================")
    print("DONE")
    print("Added:", added_count)
    print("Skipped:", skipped_count)


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    run()
