import random


FORMATS = [
    "standard",       # current format
    "quick_take",     # short, sharp
    "prediction",     # % driven
    "breakdown",      # analysis heavy
    "carousel"        # multi-slide (future)
]


def choose_format(item):

    context = item.get("context", "")
    score = item.get("score", 0)
    confidence = item.get("confidence")

    # -----------------------------
    # PREVIEW → PREDICTION
    # -----------------------------
    if context == "preview":
        return "prediction"

    # -----------------------------
    # HIGH SCORE → BREAKDOWN
    # -----------------------------
    if score > 40:
        return "breakdown"

    # -----------------------------
    # HIGH CONFIDENCE → PREDICTION
    # -----------------------------
    if confidence and confidence.get("level") == "high":
        return "prediction"

    # -----------------------------
    # DEFAULT MIX
    # -----------------------------
    return random.choice(["standard", "quick_take"])