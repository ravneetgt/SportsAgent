from fetch_news import fetch_news
from generate_caption import generate_caption
from create_post import create_post
from push_to_sheet import push_if_new
from rank_news import rank_news


def get_style(category):
    if category == "cricket":
        return "analytical_india"
    elif category == "football":
        return "transfer_drama"
    elif category == "tennis":
        return "elite_rivalry"
    elif category == "f1":
        return "precision_drama"
    return "general"


def run():
    print("RUNNING MAIN...")

    # Step 1: Fetch news
    news = fetch_news()
    print("Articles fetched:", len(news))

    if len(news) == 0:
        print("No articles returned.")
        return

    # Step 2: Rank and select top articles
    news = rank_news(news, top_n=6)
    print("Top articles selected:", len(news))

    added = 0

    # Step 3: Process each article
    for index, article in enumerate(news):
        try:
            category = article.get("category")
            title = article.get("title")
            summary = article.get("summary")

            print("\n----------------------")
            print("CATEGORY:", category)
            print("TITLE:", title)

            # Step 4: Generate caption
            style = get_style(category)

            caption = generate_caption(
                title,
                summary,
                category,
                style
            )

            print("CAPTION:\n", caption)

            # Step 5: Create branded image
            image_path = create_post(
                title,
                caption,
                category,
                index
            )

            print("IMAGE CREATED:", image_path)

            # Step 6: Push to Google Sheet
            row = [
                category,
                title,
                caption,
                image_path,
                "PENDING"
            ]

            if push_if_new(row):
                added += 1

        except Exception as e:
            print("ERROR processing article:", e)

    print("\nNew rows added:", added)


if __name__ == "__main__":
    run()
