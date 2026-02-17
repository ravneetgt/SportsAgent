import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SHEET_NAME = "Sports AI Content"


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).sheet1


def existing_titles(sheet):
    values = sheet.col_values(2)
    return set(v.strip() for v in values if v)


def push_if_new(article, caption, image_url):
    sheet = get_sheet()
    titles = existing_titles(sheet)

    title = article["title"].strip()

    if title in titles:
        print("SKIP:", title[:60])
        return False

    # -----------------------------
    # TIMESTAMP (IMPORTANT)
    # -----------------------------
    timestamp = int(datetime.utcnow().timestamp())

    row = [
        article.get("category", ""),
        title,
        caption,
        image_url,
        "PENDING",
        timestamp
    ]

    sheet.append_row(row)

    print("ADDED:", title[:60])

    return True
