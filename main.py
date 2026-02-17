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

    for article in news:
        print("\n========================")
        print("TITLE:", article["title"])

        try:
            caption = generate_caption(
                article["title"],
                article["summary"],
                article["category"]
            )

            image_url = get_image(article["query"])

            push_if_new(article, caption, image_url)

        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    run()
