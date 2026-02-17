from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image
from create_post import create_post


def run():
    print("\nRUNNING MAIN...\n")

    news = fetch_news()

    print("Articles found:", len(news))

    for article in news:
        try:
            print("\n========================")

            # Step 1: Caption
            caption = generate_caption(
                article["title"],
                article["summary"],
                article["category"]
            )

            # Step 2: Image
            image_url = get_image(article["query"])

            # Step 3: Create branded post
            final_image = create_post(
                image_url,
                article["title"],
                caption
            )

            print("CATEGORY:", article["category"])
            print("TITLE:", article["title"])
            print("QUERY:", article["query"])
            print("IMAGE:", final_image)

        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    run()
