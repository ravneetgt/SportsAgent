import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PEXELS_API_KEY")


# Build smarter search query
def build_query(title, category, keyword):
    title_lower = title.lower()

    # Cricket logic
    if category == "cricket":
        if "india" in title_lower:
            return "india cricket team match"
        if "pakistan" in title_lower:
            return "pakistan cricket team match"
        if "australia" in title_lower:
            return "australia cricket team match"
        if "england" in title_lower:
            return "england cricket team match"

        return "cricket match stadium action"

    # Football logic
    if category == "football":
        if "arsenal" in title_lower:
            return "arsenal football match"
        if "chelsea" in title_lower:
            return "chelsea football match"
        if "liverpool" in title_lower:
            return "liverpool football match"
        if "manchester united" in title_lower:
            return "manchester united football match"
        if "barcelona" in title_lower:
            return "barcelona football match"
        if "real madrid" in title_lower:
            return "real madrid football match"

        return "football stadium match action"

    return keyword


def get_image(title, category, keyword):
    if not API_KEY:
        print("PEXELS_API_KEY missing")
        return None

    query = build_query(title, category, keyword)

    print("IMAGE QUERY:", query)

    url = "https://api.pexels.com/v1/search"

    params = {
        "query": query,
        "per_page": 5,
        "orientation": "landscape"
    }

    headers = {
        "Authorization": API_KEY
    }

    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()

        photos = data.get("photos", [])

        if not photos:
            print(f"No image found for: {query}")
            return None

        # pick best result (not always first)
        for p in photos:
            if p.get("src") and p["src"].get("large"):
                return p["src"]["large"]

        return photos[0]["src"]["large"]

    except Exception as e:
        print("Image error:", e)
        return None


# test
if __name__ == "__main__":
    print(get_image(
        "India beat Pakistan in T20 World Cup",
        "cricket",
        "india"
    ))
