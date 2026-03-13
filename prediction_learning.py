import json
import os

MODEL_FILE = "prediction_model.json"


DEFAULT_MODEL = {
    "form_weight": 0.6,
    "goal_weight": 0.4,
    "home_advantage": 1.2,
    "accuracy_history": []
}


def load_model():

    if not os.path.exists(MODEL_FILE):
        return DEFAULT_MODEL

    try:
        with open(MODEL_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_MODEL


def save_model(model):

    try:
        with open(MODEL_FILE, "w") as f:
            json.dump(model, f)
    except:
        pass


def record_result(predicted_home_pct, actual_home_win):

    model = load_model()

    correct = (
        predicted_home_pct > 50 and actual_home_win
    ) or (
        predicted_home_pct <= 50 and not actual_home_win
    )

    model["accuracy_history"].append(1 if correct else 0)

    if len(model["accuracy_history"]) > 100:
        model["accuracy_history"] = model["accuracy_history"][-100:]

    accuracy = sum(model["accuracy_history"]) / len(model["accuracy_history"])

    if accuracy < 0.55:
        model["form_weight"] += 0.05
        model["goal_weight"] -= 0.05

    save_model(model)


def get_weights():

    model = load_model()

    return (
        model["form_weight"],
        model["goal_weight"],
        model["home_advantage"]
    )