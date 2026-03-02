import random


PERSONALITIES = [
    "analyst",     # current default
    "insider",     # dressing-room tone
    "contrarian",  # challenges consensus
    "cultural",    # narrative, cinematic
    "fan"          # emotional spike
]


def choose_personality(item):

    context = item.get("context", "")
    score = item.get("score", 0)
    confidence = item.get("confidence")

    # -----------------------------
    # HIGH IMPORTANCE → STRONG VOICE
    # -----------------------------
    if score > 40:
        return random.choice(["analyst", "insider", "contrarian"])

    # -----------------------------
    # PREVIEW → ANALYST
    # -----------------------------
    if context == "preview":
        return "analyst"

    # -----------------------------
    # CONTROVERSY → CONTRARIAN
    # -----------------------------
    title = item.get("title", "").lower()
    if any(k in title for k in ["racism", "ban", "charge"]):
        return "contrarian"

    # -----------------------------
    # LOW CONFIDENCE → CULTURAL
    # -----------------------------
    if confidence and confidence.get("level") == "low":
        return "cultural"

    # -----------------------------
    # DEFAULT MIX
    # -----------------------------
    return random.choice(PERSONALITIES)