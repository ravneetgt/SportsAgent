from store import load_store


def compute_power_rankings() -> list:
    store    = load_store()
    rankings = []

    for team, data in store.items():
        form = data.get("recent_form", [])

        if len(form) < 5:
            continue

        score = form.count("W") * 3 + form.count("D")
        rankings.append((team, score))

    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings[:10]


def build_power_post() -> tuple:
    rankings = compute_power_rankings()

    if not rankings:
        return None, None

    lines = [f"{i+1}. {team} ({score})" for i, (team, score) in enumerate(rankings)]

    return "GLOBAL FORM INDEX", "\n".join(lines)