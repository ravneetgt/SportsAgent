import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

SHEET_NAME = "Sports AI Content"


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # LOCAL
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )
    else:
        # STREAMLIT CLOUD
        import streamlit as st
        creds_dict = dict(st.secrets["gcp_service_account"])

        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            creds_dict, scope
        )

    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1

    print("Connected to sheet:", SHEET_NAME)
    return sheet


def existing_titles(sheet):
    try:
        values = sheet.col_values(2)
        return set(v.strip() for v in values if v)
    except Exception as e:
        print("Error fetching titles:", e)
        return set()


def is_duplicate(title, titles):
    # fuzzy match instead of exact match
    for t in titles:
        if title[:60] in t:
            return True
    return False


def push_if_new(article, caption, image_url):
    try:
        sheet = get_sheet()

        titles = existing_titles(sheet)

        title = article["title"].strip()

        print("\nChecking:", title[:60])

        if is_duplicate(title, titles):
            print("SKIP (duplicate):", title[:60])
            return False

        row = [
            article["category"],
            article["title"],
            caption,
            image_url if image_url else "",
            "PENDING"
        ]

        print("Appending row...")

        sheet.append_row(row)

        print("SUCCESS:", title[:60])
        return True

    except Exception as e:
        print("PUSH ERROR:", e)
        return False
