from fetch_news import fetch_news
from generate_caption import generate_caption
from get_image import get_image

import re


# -----------------------------
# EXTRACT KEY ENTITIES
# -----------------------------
def extract_entities(title):
    words = re.findall(r'\b[A-Z][a-zA-Z]+\b', title)
    return " ".join(words[:3])


# -----------------------------
# BUILD IMAGE QUERY
# -----------------------------
def build_image_query(article):
    title = article["title"]
    category = article["category"]

    entities = extract_entities(title)

    if category == "football":
        return f"{entities} football match stadium players"

    elif category == "cricket":
        return f"{entities} cricket match batsman bowler"

    elif category == "tennis":
        return f"{entities} tennis match player court"

    elif category == "f1":
        return f"{entities} formula 1 race car"

    return f"{entities} {category}"


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run():
    print("\nRUNNING MAIN...")

    news = fetch_news()

    if not news:
        print("No articles found.")
        return

    print("Articles found:", len(news))

    for article in news:
        print("\n========================")

        try:
            # Extract data
            title = article["title"]
            summary = article["summary"]
            category = article["category"]

            # Debug
            print("CATEGORY:", category)
            print("TITLE:", title)

            # -----------------------------
            # CAPTION
            # -----------------------------
            caption = generate_caption(
                title,
                summary,
                category
            )

            # -----------------------------
            # IMAGE
            # -----------------------------
            query = build_image_query(article)
            image_url = get_image(query)

            # -----------------------------
            # OUTPUT
            # -----------------------------
            print("\nCAPTION:\n", caption)

            print("\nIMAGE QUERY:", query)
            print("IMAGE URL:", image_url)

        except Exception as e:
            print("ERROR:", e)
            continue


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    run()
