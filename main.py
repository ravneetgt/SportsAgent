import time

from fetch_news import fetch_news
from fetch_fixtures import fetch_fixtures
from rank_news import rank_news
from generate_caption import generate_content
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new


def run():
    print("=== START ===")

    news = fetch_news()

    if not news:
        print("No news")
        return

    ranked = rank_news(news)

    for article in ranked[:8]:

        try:
            title = article["title"]
            summary = article.get("summary", "")
            category = article.get("category", "football")
            context = article.get("context", "news")
            score = article.get("score", 0)

            print("Processing:", title)

            content = generate_content(
                title=title,
                summary=summary,
                category=category,
                context=context
            )

            short_caption = content.get("short_caption", "")
            long_caption = content.get("long_caption", "")
            article_text = content.get("article", "")

            image_url = get_image(title)

            if not image_url:
                continue

            try:
                final_image_url = create_post(
                    image_url=image_url,
                    title=title,
                    caption=short_caption
                )
            except Exception as e:
                print("Image error:", e)
                final_image_url = image_url

            push_if_new({
                "Type": "instagram",
                "Category": category,
                "Title": title,
                "Short Caption": short_caption,
                "Long Caption": long_caption,
                "Article": "",
                "Image URL": final_image_url,
                "Status": "PENDING",
                "Context": context,
                "Score": score,
                "Date": int(time.time())
            })

            push_if_new({
                "Type": "article",
                "Category": category,
                "Title": title,
                "Short Caption": short_caption,
                "Long Caption": long_caption,
                "Article": article_text,
                "Image URL": image_url,
                "Status": "PENDING",
                "Context": context,
                "Score": score,
                "Date": int(time.time())
            })

            print("✓ Done")

        except Exception as e:
            print("ERROR TYPE:", type(e))
            print("ERROR VALUE:", str(e))


if __name__ == "__main__":
    run()