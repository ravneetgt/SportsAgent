import json
import os

MODEL_FILE = "prediction_model.json"


# --------------------------------------------------
# home_advantage was 1.2 — far too large.
# At 1.2 it shifts home win probability by ~18 points
# before any form data is considered, making away
# favourites appear as draws and home underdogs as
# favourites. Real-world home advantage is ~5-8%.
# 0.08 shifts probability by roughly 2 points, which
# is accurate for modern elite football.
# --------------------------------------------------

DEFAULT_MODEL = {
    "form_weight":      0.6,
    "goal_weight":      0.4,
    "home_advantage":   0.08,   # was 1.2 — fixed
    "accuracy_history": []
}


def load_model():
    if not os.path.exists(MODEL_FILE):
        return DEFAULT_MODEL
    try:
        with open(MODEL_FILE, "r") as f:
            model = json.load(f)
            # Force fix any existing model files with the old bad value
            if model.get("home_advantage", 0) > 0.5:
                model["home_advantage"] = 0.08
            return model
    except Exception:
        return DEFAULT_MODEL


def save_model(model):
    try:
        with open(MODEL_FILE, "w") as f:
            json.dump(model, f)
    except Exception:
        pass


def get_weights():
    model = load_model()
    return (
        model.get("form_weight",    0.6),
        model.get("goal_weight",    0.4),
        model.get("home_advantage", 0.08),
    )


def record_result(predicted_home_pct, actual_home_win):
    """
    Records whether a prediction was correct.
    Used by the learning loop to track model accuracy over time.
    """
    model = load_model()

    correct = (
        (predicted_home_pct > 50 and actual_home_win) or
        (predicted_home_pct <= 50 and not actual_home_win)
    )

    model["accuracy_history"].append(1 if correct else 0)

    # Keep only last 100 results
    if len(model["accuracy_history"]) > 100:
        model["accuracy_history"] = model["accuracy_history"][-100:]

    accuracy = sum(model["accuracy_history"]) / len(model["accuracy_history"])

    # Nudge weights based on accuracy
    if accuracy < 0.45:
        # Underperforming — reduce form weight, increase goals weight
        model["form_weight"] = max(0.3, model["form_weight"] - 0.02)
        model["goal_weight"] = min(0.7, model["goal_weight"] + 0.02)
    elif accuracy > 0.60:
        # Overperforming — strengthen form weight slightly
        model["form_weight"] = min(0.8, model["form_weight"] + 0.01)

    save_model(model)
    return accuracy


def get_accuracy() -> float:
    """Returns current model accuracy as a float 0–1."""
    model = load_model()
    history = model.get("accuracy_history", [])
    if not history:
        return 0.0
    return round(sum(history) / len(history), 3)


def accuracy_label() -> str:
    """Returns human-readable accuracy label for display."""
    acc = get_accuracy()
    pct = int(acc * 100)
    if pct >= 65:
        band = "HIGH"
    elif pct >= 50:
        band = "MODERATE"
    else:
        band = "LOW — model still learning"
    return f"{pct}% accuracy ({len(load_model().get('accuracy_history', []))} predictions)"