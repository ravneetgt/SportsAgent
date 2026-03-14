"""
store.py
--------
Single source of truth for memory_store.json access.
Replaces load_store() / save_store() duplicated across
team_intelligence_engine, daily_edge_index, league_intelligence,
narrative_memory, and predictive_edge_engine.
"""

import json
import os

STORE_PATH = "memory_store.json"


def load_store() -> dict:
    if not os.path.exists(STORE_PATH):
        return {}
    try:
        with open(STORE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_store(store: dict) -> None:
    try:
        with open(STORE_PATH, "w") as f:
            json.dump(store, f, indent=2)
    except Exception as e:
        print("Store save error:", e)