import gspread
import streamlit as st
import time
import os
from oauth2client.service_account import ServiceAccountCredentials

SPREADSHEET_ID = "1eQwoa3etxf3g82jZop50lt598NJRCZ2bHRUUMQDsSOw"
WORKSHEET_NAME = "Sheet1"


def get_creds(scope):
    # LOCAL RUN
    if os.path.exists("credentials.json"):
        print("Using local credentials.json")
        return ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )

    # STREAMLIT CLOUD
    if "gcp_service_account" in st.secrets:
        print("Using Streamlit secrets")
        return ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["gcp_service_account"], scope
        )

    raise Exception("No credentials found. Add credentials.json or Streamlit secrets.")


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = get_creds(scope)

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    return spreadsheet.worksheet(WORKSHEET_NAME)
def push_if_new(row):
    try:
        sheet = get_sheet()

        # -----------------------------
        # DUPLICATE CHECK
        # -----------------------------
        titles = sheet.col_values(3)

        if row.get("Title") in titles:
            print("SKIP:", row.get("Title")[:60])
            return False

        # -----------------------------
        # BUILD ROW
        # -----------------------------
        values = [
            row.get("Type", ""),
            row.get("Category", ""),
            row.get("Title", ""),
            row.get("Short Caption", ""),
            row.get("Long Caption", ""),
            row.get("Article", ""),
            row.get("Image URL", ""),
            row.get("Status", "PENDING"),
            row.get("Context", ""),
            row.get("Score", 0),
            row.get("Date", int(time.time()))
        ]

        print("ADDING:", row.get("Title")[:60])

        sheet.append_row(values, table_range="A1:K1")

        print("ADDED SUCCESSFULLY")

        return True

    except Exception as e:
        print("Sheet push error:", str(e))
        return False