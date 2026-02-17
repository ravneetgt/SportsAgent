from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new
from rank_news import rank_news
from upload_image import upload_image
import time


def run():
    print("Starting pipeline...")

    news = fetch_news()

    print("Fetched:", len(news))

    news = rank_news(news)

    for i, article in enumerate(news):
        try:
            title = article["title"]
            category = article["category"]

            print("\nProcessing:", title[:60])

            # caption
            caption = generate_caption(title)

            # image search
            query = f"{category} sports action"
            image_url = get_image(query)

            if not image_url:
                print("No image")
                continue

            # create post
            filename = f"post_{int(time.time())}.jpg"

            post_path = create_post(
                image_url=image_url,
                title=title,
                caption=caption,
                filename=filename
            )

            if not post_path:
                print("Post creation failed")
                continue

            # upload image
            public_url = upload_image(post_path)

            if not public_url:
                print("Upload failed")
                continue

            # timestamp
            timestamp = int(time.time())

            row = [
                category,
                title,
                caption,
                public_url,
                "PENDING",
                timestamp
            ]

            push_if_new(row)

        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    run()
