import os
import requests

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


# -----------------------------
# BUILD SMART QUERY
# -----------------------------
def build_query(item):
    title = item.get("title", "")
    context = item.get("context", "")
    teams = item.get("teams")

    # If custom query already exists (fixtures)
    if item.get("query"):
        return item["query"]

    # -----------------------------
    # MATCHES (BEST CASE)
    # -----------------------------
    if teams and len(teams) == 2:
        return f"{teams[0]} vs {teams[1]} football match players stadium"

    # -----------------------------
    # TRANSFERS
    # -----------------------------
    if "transfer" in title.lower():
        return f"{title} football player portrait jersey"

    # -----------------------------
    # INJURIES / INCIDENTS
    # -----------------------------
    if "injury" in title.lower() or "ban" in title.lower():
        return f"{title} football player match action"

    # -----------------------------
    # DEFAULT
    # -----------------------------
    return f"{title} football soccer player action match"


# -----------------------------
# FETCH IMAGE FROM PEXELS
# -----------------------------
def get_image(item):

    query = build_query(item) + " soccer"

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 6
    }

    try:
        res = requests.get(url, headers=headers, params=params)

        print("IMAGE QUERY:", query)
        print("Pexels status:", res.status_code)

        if res.status_code != 200:
            return None

        data = res.json()
        photos = data.get("photos", [])

        if not photos:
            return None

        # -----------------------------
        # PRIORITY 1: FOOTBALL TAGS
        # -----------------------------
        for p in photos:
            alt = (p.get("alt") or "").lower()

            if "football" in alt or "soccer" in alt:
                return p["src"]["large"]

        # -----------------------------
        # PRIORITY 2: LANDSCAPE ACTION
        # -----------------------------
        for p in photos:
            if p["width"] > p["height"]:
                return p["src"]["large"]

        # -----------------------------
        # FALLBACK
        # -----------------------------
        return photos[0]["src"]["large"]

    except Exception as e:
        print("get_image error:", str(e))
        return None