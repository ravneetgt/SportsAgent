import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PEXELS_API_KEY")


def get_image(query):
    if not API_KEY:
        print("PEXELS_API_KEY missing")
        return None

    # Improve query quality
    enhanced_query = f"{query} sports action"

    url = "https://api.pexels.com/v1/search"

    params = {
        "query": enhanced_query,
        "per_page": 5,
        "orientation": "portrait"
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

        return photos[0]["src"]["large"]

    except Exception as e:
        print("Image error:", e)
        return None


# test
if __name__ == "__main__":
    print(get_image("India vs Australia cricket"))
