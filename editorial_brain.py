def build_editorial_context(item: dict) -> dict:

    title      = item.get("title", "").lower()
    context    = item.get("context", "news")
    confidence = item.get("confidence")
    narrative  = item.get("narrative", "")
    score      = item.get("score", 0)

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
    # Thresholds match rank_news scoring reality (max ~45).
    # high  > 25 — strong result or breaking news about big club
    # medium > 12 — typical well-scored item
    # low    ≤ 12 — generic content
    # -----------------------------
    if score > 25:
        priority = "high"
    elif score > 12:
        priority = "medium"
    else:
        priority = "low"

    # -----------------------------
    # ANGLE — priority now influences selection
    # -----------------------------
    angle = item.get("angle", "narrative")

    if story_type == "result":
        angle = "trend" if narrative else "result_shift"

    elif story_type == "preview":
        if confidence and confidence.get("level") == "high":
            angle = "edge"
        else:
            angle = "matchup"

    elif story_type == "controversy":
        angle = "pressure"

    elif story_type == "analysis":
        # Priority drives angle for generic analysis pieces
        if priority == "high":
            angle = "deep_analysis"
        elif priority == "medium":
            angle = "narrative"
        else:
            angle = "observation"

    return {
        "story_type": story_type,
        "tone":       tone,
        "priority":   priority,
        "angle":      angle,
        "narrative":  narrative,
        "confidence": confidence
    }