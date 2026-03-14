"""
sheets_client.py
----------------
Single source of truth for Google Sheets access.
Used by both app.py (Streamlit) and push_to_sheet.py (pipeline).

Credential resolution order:
  1. credentials.json  — local dev
  2. GOOGLE_CREDS_JSON — env var containing the JSON string (CI / cron)
  3. st.secrets        — Streamlit Cloud (only attempted if streamlit is importable)
"""

import gspread
import json
import os
import time
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1eQwoa3etxf3g82jZop50lt598NJRCZ2bHRUUMQDsSOw")
WORKSHEET_NAME = "Sheet1"

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


def get_creds():
    # 1. Local file
    if os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)

    # 2. Environment variable (for cron / CI environments)
    raw = os.getenv("GOOGLE_CREDS_JSON")
    if raw:
        try:
            info = json.loads(raw)
            return ServiceAccountCredentials.from_json_keyfile_dict(info, SCOPE)
        except Exception as e:
            print("GOOGLE_CREDS_JSON parse error:", e)

    # 3. Streamlit secrets (only when running inside Streamlit)
    try:
        import streamlit as st
        if "gcp_service_account" in st.secrets:
            return ServiceAccountCredentials.from_json_keyfile_dict(
                st.secrets["gcp_service_account"], SCOPE
            )
    except Exception:
        pass

    raise Exception(
        "No Google credentials found. Provide credentials.json, "
        "GOOGLE_CREDS_JSON env var, or st.secrets['gcp_service_account']."
    )


def get_sheet():
    creds  = get_creds()
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
