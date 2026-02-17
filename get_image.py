import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PEXELS_API_KEY")


def get_image(query):
    if not API_KEY:
        print("PEXELS_API_KEY missing")
        return None

    url = "https://api.pexels.com/v1/search"

    params = {
        "query": f"{query} sports action",
        "per_page": 3,
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
            print("No image found")
            return None

        return photos[0]["src"]["large"]

    except Exception as e:
        print("Image error:", e)
        return None
