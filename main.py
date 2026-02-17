from fetch_news import fetch_news
from rank_news import rank_news
from generate_caption import generate_caption
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new
from upload_image import upload_image

import time
import os


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run():
    print("\n=== SPORTS AGENT START ===\n")

    # Step 1: Fetch news
    articles = fetch_news()

    if not articles:
        print("No articles found")
        return

    print(f"Fetched {len(articles)} articles")

    # Step 2: Rank news
    articles = rank_news(articles)

    print(f"Processing top {len(articles)} articles\n")

    # Step 3: Process each article
    for i, article in enumerate(articles):
        try:
            print(f"\nProcessing {i+1}/{len(articles)}")

            title = article.get("title", "")
            summary = article.get("summary", "")
            category = article.get("category", "")
            link = article.get("link", "")

            print("Title:", title)

            # -----------------------------
            # Step 4: Generate caption
            # -----------------------------
            caption = generate_caption(title, summary, category)

            if not caption:
                print("Skipping (no caption)")
                continue

            # -----------------------------
            # Step 5: Get image
            # -----------------------------
            image_url = get_image(title + " " + category)

            if not image_url:
                print("Skipping (no image)")
                continue

            # -----------------------------
            # Step 6: Create post image
            # -----------------------------
            filename = f"posts/post_{int(time.time())}.jpg"

            create_post(image_url, caption, filename)

            # -----------------------------
            # Step 7: Upload image (Cloudinary)
            # -----------------------------
            uploaded_url = upload_image(filename)

            if not uploaded_url:
                print("Skipping (upload failed)")
                continue

            # -----------------------------
            # Step 8: Save to Google Sheets
            # -----------------------------
            timestamp = int(time.time())

            row = [
                category,
                title,
                caption,
                uploaded_url,
                "PENDING",
                timestamp,
                link
            ]

            push_if_new(row)

            print("Done")

        except Exception as e:
            print("ERROR:", e)

    print("\n=== DONE ===\n")


# -----------------------------
# RUN DIRECTLY
# -----------------------------
if __name__ == "__main__":
    run()
