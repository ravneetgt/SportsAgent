import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_NAME = "Sports AI Content"


# -----------------------------
# CONNECT TO SHEET
# -----------------------------
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


# -----------------------------
# GET EXISTING TITLES (DEDUP)
# -----------------------------
def existing_titles(sheet):
    try:
        values = sheet.col_values(2)  # Column B = Title
        return set(v.strip() for v in values if v)
    except Exception as e:
        print("Error reading titles:", e)
        return set()


# -----------------------------
# PUSH ROW IF NEW
# -----------------------------
def push_if_new(row):
    try:
        sheet = get_sheet()

        titles = existing_titles(sheet)

        title = str(row[1]).strip()

        if title in titles:
            print("SKIP (duplicate):", title[:60])
            return False

        sheet.append_row(row)
        print("ADDED:", title[:60])

        return True

    except Exception as e:
        print("Sheet push error:", e)
        return False
