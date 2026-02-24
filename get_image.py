import os
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def get_image(query):
    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 5
    }

    try:
        res = requests.get(url, headers=headers, params=params)

        # DEBUG
        print("Pexels status:", res.status_code)

        if res.status_code != 200:
            return None

        data = res.json()

        photos = data.get("photos", [])

        if not photos:
            return None

        return photos[0]["src"]["large"]

    except Exception as e:
        print("get_image error:", str(e))
        return None