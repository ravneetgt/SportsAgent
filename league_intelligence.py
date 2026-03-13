import json

STORE_PATH = "memory_store.json"


def load_store():

    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def compute_power_rankings():

    store = load_store()

    rankings = []

    for team, data in store.items():

        form = data.get("recent_form", [])

        if len(form) < 5:
            continue

        score = form.count("W") * 3 + form.count("D")

        rankings.append((team, score))

    rankings.sort(key=lambda x: x[1], reverse=True)

    return rankings[:10]


def build_power_post():

    rankings = compute_power_rankings()

    if not rankings:
        return None, None

    lines = []

    for i, (team, score) in enumerate(rankings):
        lines.append(f"{i+1}. {team} ({score})")

    overlay = "GLOBAL FORM INDEX"

    return overlay, "\n".join(lines)