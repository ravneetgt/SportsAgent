# -----------------------------
# EDITORIAL BRAIN
# -----------------------------
def build_editorial_context(item):

    title = item.get("title", "").lower()
    context = item.get("context", "news")
    insight = item.get("insight")
    confidence = item.get("confidence")
    narrative = item.get("narrative", "")
    score = item.get("score", 0)

    # -----------------------------
    # STORY TYPE
    # -----------------------------
    story_type = "analysis"

    if any(k in title for k in ["beat", "win", "defeat"]):
        story_type = "result"

    if "transfer" in title:
        story_type = "transfer"

    if any(k in title for k in ["racism", "ban", "charge"]):
        story_type = "controversy"

    if context == "preview":
        story_type = "preview"

    # -----------------------------
    # TONE
    # -----------------------------
    tone = "balanced"

    if confidence:
        gap = abs(confidence.get("home_pct", 50) - confidence.get("away_pct", 50))

        if gap > 25:
            tone = "confident"
        elif gap < 10:
            tone = "uncertain"

    # -----------------------------
    # PRIORITY
    # -----------------------------
    if score > 40:
        priority = "high"
    elif score > 20:
        priority = "medium"
    else:
        priority = "low"

    # -----------------------------
    # ANGLE OVERRIDE
    # -----------------------------
    angle = item.get("angle", "narrative")

    if story_type == "result":
        if narrative:
            angle = "trend"
        else:
            angle = "result_shift"

    if story_type == "preview":
        if confidence and confidence.get("level") == "high":
            angle = "edge"
        else:
            angle = "matchup"

    if story_type == "controversy":
        angle = "pressure"

    # -----------------------------
    # BUILD CONTEXT
    # -----------------------------
    editorial = {
        "story_type": story_type,
        "tone": tone,
        "priority": priority,
        "angle": angle,
        "narrative": narrative,
        "confidence": confidence
    }

    return editorial