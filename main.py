import time
import requests

from fetch_news import fetch_news
from rank_news import rank_news
from generate_caption import generate_content
from get_image import get_image
from create_post import create_post
from push_to_sheet import push_if_new


def download_image(url, path="temp.jpg"):
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            with open(path, "wb") as f:
                f.write(res.content)
            return path
        else:
            print("Image download failed:", res.status_code)
            return None
    except Exception as e:
        print("Download error:", e)
        return None


def run():
    print("=== START ===")

    news = fetch_news()

    if not news:
        print("No news found")
        return

    ranked = rank_news(news)

    for item in ranked:

        try:
            title = item.get("title", "")
            summary = item.get("summary", "")
            category = item.get("category", "football")
            context = item.get("context", "general")
            score = item.get("score", 0)

            print("Processing:", title)

            # -----------------------------
            # GENERATE CONTENT
            # -----------------------------
            short_caption, long_caption, article = generate_content(
                title,
                summary,
                category,
                context
            )

            # -----------------------------
            # GET IMAGE URL
            # -----------------------------
            image_url = get_image(title)

            local_image_path = None
            final_image_path = None

            if image_url:
                print("Pexels status: 200")

                # download image
                local_image_path = download_image(image_url)

                if local_image_path:
                    try:
                        print("create_post called")

                        final_image_path = "post.jpg"

                        create_post(
                            image_path=local_image_path,
                            title=title,
                            caption=short_caption,
                            output_path=final_image_path
                        )

                    except Exception as e:
                        print("Image error:", e)

            # -----------------------------
            # USE FINAL IMAGE (UPLOAD STEP)
            # -----------------------------
            final_url = image_url  # fallback

            try:
                if final_image_path:
                    # upload to cloudinary (you already have this)
                    from upload_image import upload_image

                    final_url = upload_image(final_image_path)
                    print("Uploaded:", final_url)

            except Exception as e:
                print("Upload error:", e)

            # -----------------------------
            # PUSH INSTAGRAM POST
            # -----------------------------
            push_if_new({
                "Type": "instagram",
                "Category": category,
                "Title": title,
                "Short Caption": short_caption,
                "Long Caption": long_caption,
                "Article": "",
                "Image URL": final_url,
                "Status": "PENDING",
                "Context": context,
                "Score": score,
                "Date": int(time.time())
            })

            # -----------------------------
            # PUSH ARTICLE
            # -----------------------------
            push_if_new({
                "Type": "article",
                "Category": category,
                "Title": title,
                "Short Caption": short_caption,
                "Long Caption": long_caption,
                "Article": article,
                "Image URL": final_url,
                "Status": "PENDING",
                "Context": context,
                "Score": score,
                "Date": int(time.time())
            })

            print("✓ Done")

        except Exception as e:
            print("ERROR:", e)


if __name__ == "__main__":
    run()