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
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


def existing_titles(sheet):
    # read column B (Title) to avoid duplicates
    values = sheet.col_values(2)  # 1-based index
    return set(v.strip() for v in values if v)


def push_row(row):
    sheet = get_sheet()
    sheet.append_row(row)


def push_if_new(row):
    sheet = get_sheet()
    titles = existing_titles(sheet)
    title = row[1].strip()

    if title in titles:
        print("SKIP (duplicate):", title[:60])
        return False

    sheet.append_row(row)
    print("ADDED:", title[:60])
    return True
