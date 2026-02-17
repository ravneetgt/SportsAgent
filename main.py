from fetch_news import fetch_news
from rank_news import rank_news
from generate_caption import generate_caption
from get_image import get_image
from create_post import create_post
from upload_image import upload_image
from push_to_sheet import push_if_new

import time
import os


def run():
    print("\n=== START ===\n")

    articles = fetch_news()

    if not articles:
        print("No news found")
        return

    articles = rank_news(articles)

    print("Articles:", len(articles))

    for i, article in enumerate(articles):
        try:
            print("\n----------------------")
            print(f"Processing {i+1}/{len(articles)}")

            title = article.get("title", "")
            summary = article.get("summary", "")
            category = article.get("category", "")

            print("Title:", title)

            # -----------------------------
            # CAPTION
            # -----------------------------
            caption = generate_caption(title, summary, category)

            if not caption:
                print("No caption")
                continue

            # -----------------------------
            # IMAGE SEARCH
            # -----------------------------
            image_url = get_image(title, category)

            if not image_url:
                print("No image")
                continue

            # -----------------------------
            # CREATE POST IMAGE
            # -----------------------------
            filename = f"posts/post_{int(time.time())}.jpg"

            post_path = create_post(
                image_url,
                title,
                caption,
                filename
            )

            if not post_path:
                print("Create post failed")
                continue

            print("File exists:", os.path.exists(post_path))

            # -----------------------------
            # UPLOAD
            # -----------------------------
            uploaded_url = upload_image(post_path)

            if not uploaded_url:
                print("Upload failed")
                continue

            print("UPLOADED:", uploaded_url)

            # -----------------------------
            # SAVE TO SHEET
            # -----------------------------
            timestamp = int(time.time())

            row = [
                category,
                title,
                caption,
                uploaded_url,
                "PENDING",
                timestamp
            ]

            push_if_new(row)

            print("Done")

        except Exception as e:
            print("ERROR:", e)

    print("\n=== DONE ===\n")


if __name__ == "__main__":
    run()
