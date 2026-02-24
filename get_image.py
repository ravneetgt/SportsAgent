import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------
# GPT QUERY GENERATOR (IMPROVED)
# -----------------------------
def generate_image_query(title, category):
    try:
        prompt = f"""
Generate a realistic editorial sports photography search query.

SPORT: {category}

RULES:
- Must look like a real sports photograph
- Prefer player action, stadium, or match moment
- Avoid generic words like "news" or "sports"
- Avoid words like "illustration" or "graphic"
- 6 to 8 words

TITLE: {title}

Return ONLY the query.
"""

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        query = res.choices[0].message.content.strip()

        print("GPT QUERY:", query)

        return query

    except Exception as e:
        print("GPT error:", e)
        return title


# -----------------------------
# SEARCH PEXELS
# -----------------------------
def search_pexels(query):
    url = "https://api.pexels.com/v1/search"

    params = {
        "query": query,
        "per_page": 10,
        "orientation": "portrait"
    }

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    return data.get("photos", [])


# -----------------------------
# PICK BEST IMAGE
# -----------------------------
def pick_best_photo(photos):
    if not photos:
        return None

    # Prefer larger / high-quality images
    sorted_photos = sorted(
        photos,
        key=lambda p: p.get("width", 0),
        reverse=True
    )

    return sorted_photos[0]


# -----------------------------
# GET IMAGE
# -----------------------------
def get_image(title, category):
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY missing")
        return None

    try:
        # -----------------------------
        # 1. GPT QUERY
        # -----------------------------
        query = generate_image_query(title, category)

        photos = search_pexels(query)

        # -----------------------------
        # 2. CATEGORY FALLBACK
        # -----------------------------
        if not photos:
            print("Fallback category")

            fallback_queries = {
                "football": [
                    "football match action stadium players",
                    "soccer goal celebration crowd stadium",
                    "football players tackling match action"
                ]
            }

            for q in fallback_queries.get(category, []):
                photos = search_pexels(q)
                if photos:
                    break

        # -----------------------------
        # 3. GENERIC FALLBACK
        # -----------------------------
        if not photos:
            print("Fallback generic")
            photos = search_pexels("football match stadium crowd")

        if not photos:
            print("No images found")
            return None

        # -----------------------------
        # 4. PICK BEST
        # -----------------------------
        best = pick_best_photo(photos)

        if not best:
            return None

        return best["src"]["large"]

    except Exception as e:
        print("Image error:", e)
        return None


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    print(get_image("Manchester United vs Arsenal preview", "football"))
