from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image
from push_to_sheet import push_if_new


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
            # 1. Generate caption
            caption = generate_caption(title, summary, category)

            print("\nCAPTION:")
            print(caption)

            # 2. Get image
            image_url = get_image(query)

            print("\nIMAGE URL:", image_url)

            # 3. Push to sheet
            print("\nCalling push...")

            added = push_if_new(article, caption, image_url)

            print("Result:", added)

            if added:
                added_count += 1
            else:
                skipped_count += 1

        except Exception as e:
            print("ERROR:", e)

    print("\n========================")
    print("DONE")
    print("Added:", added_count)
    print("Skipped:", skipped_count)


if __name__ == "__main__":
    run()
