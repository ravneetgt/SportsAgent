import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
    values = sheet.col_values(2)  # Title column
    return set(v.strip() for v in values if v)


def push_if_new(category, title, caption, image_url, timestamp):
    sheet = get_sheet()
    titles = existing_titles(sheet)

    if title.strip() in titles:
        print("SKIP (duplicate):", title[:60])
        return False

    row = [
        category,
        title,
        caption,
        image_url,
        "PENDING",
        timestamp
    ]

    sheet.append_row(row)
    print("ADDED:", title[:60])
    return True
