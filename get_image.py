import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------
# GPT QUERY GENERATOR
# -----------------------------
def generate_image_query(title, category):
    try:
        prompt = f"""
Generate a realistic sports photography search query.

SPORT: {category}

RULES:
- Focus on action shot
- Include match context or player type
- Avoid generic words like "news"
- 5 to 8 words only

TITLE: {title}

Return ONLY the search query.
"""

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
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
        "per_page": 5,
        "orientation": "portrait"
    }

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    res = requests.get(url, headers=headers, params=params)
    data = res.json()

    return data.get("photos", [])


# -----------------------------
# GET IMAGE
# -----------------------------
def get_image(title, category):
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY missing")
        return None

    try:
        # -----------------------------
        # 1. SMART QUERY
        # -----------------------------
        query = generate_image_query(title, category)

        photos = search_pexels(query)

        # -----------------------------
        # 2. FALLBACKS
        # -----------------------------
        if not photos:
            print("Fallback 1")

            fallback_queries = {
                "cricket": "cricket match action stadium",
                "football": "football match action stadium",
                "tennis": "tennis match player action",
                "f1": "formula 1 race car track"
            }

            fallback = fallback_queries.get(category, "sports action")

            photos = search_pexels(fallback)

        if not photos:
            print("Fallback 2 generic")
            photos = search_pexels("sports action")

        if not photos:
            print("No images found")
            return None

        # -----------------------------
        # 3. RETURN BEST IMAGE
        # -----------------------------
        best = photos[0]

        return best["src"]["large"]

    except Exception as e:
        print("Image error:", e)
        return None


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    print(get_image("India vs Australia thriller", "cricket"))
