from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image
from create_post import create_post
from upload_image import upload_image
from push_to_sheet import push_if_new


def run():
    print("\nRUNNING MAIN...\n")

    news = fetch_news()

    if not news:
        print("No news found")
        return

    added = 0
    skipped = 0

    for i, article in enumerate(news):
        print("\n====================")
        print(f"{i+1}/{len(news)}")
        title = article.get("title", "")
        summary = article.get("summary", "")
        category = article.get("category", "")

        try:
            # 1) caption
            caption = generate_caption(title, summary, category)

            # 2) base image (pexels)
            base_url = get_image(title, category)
            if not base_url:
                print("No base image")
                skipped += 1
                continue

            # 3) create branded local image
            local_path = create_post(base_url, title, caption)
            if not local_path:
                print("Create post failed")
                skipped += 1
                continue

            # 4) upload to cloud
            public_url = upload_image(local_path)
            if not public_url:
                print("Upload failed")
                skipped += 1
                continue

            # 5) save URL (IMPORTANT)
            ok = push_if_new(article, caption, public_url)

            if ok:
                added += 1
            else:
                skipped += 1

        except Exception as e:
            print("ERROR:", e)
            skipped += 1

    print("\nDONE")
    print("Added:", added)
    print("Skipped:", skipped)


if __name__ == "__main__":
    run()
