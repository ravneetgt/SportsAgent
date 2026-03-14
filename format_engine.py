import random

FORMATS = [
    "standard",    # balanced output
    "quick_take",  # short, sharp
    "prediction",  # probability-driven
    "breakdown",   # analysis-heavy
]


def choose_format(item: dict) -> str:
    context    = item.get("context", "")
    score      = item.get("score", 0)
    confidence = item.get("confidence")

    # Fixture previews → prediction format
    if context == "preview":
        return "prediction"

    # High confidence match → prediction
    if confidence and confidence.get("level") == "high":
        return "prediction"

    # High scoring item → breakdown
    # Threshold lowered from 40 to 25 to match rank_news scoring reality
    if score > 25:
        return "breakdown"

    return random.choice(["standard", "quick_take"])