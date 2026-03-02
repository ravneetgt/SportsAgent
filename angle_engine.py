def get_angle(item):

    title = item.get("title", "").lower()
    context = item.get("context", "")
    insight = item.get("insight")

    # -----------------------------
    # RESULT → DOMINANCE / COLLAPSE
    # -----------------------------
    if any(k in title for k in ["beat", "win", "defeat"]):
        return "dominance"

    # -----------------------------
    # TRANSFER → POWER SHIFT
    # -----------------------------
    if "transfer" in title:
        return "power_shift"

    # -----------------------------
    # RACISM / CONTROVERSY
    # -----------------------------
    if any(k in title for k in ["racism", "abuse", "ban"]):
        return "controversy"

    # -----------------------------
    # PREVIEW
    # -----------------------------
    if context == "preview":
        if insight:
            return "matchup"
        return "uncertainty"

    # -----------------------------
    # DEFAULT
    # -----------------------------
    return "narrative"