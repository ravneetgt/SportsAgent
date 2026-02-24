import gspread
import time
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

    spreadsheet = client.open_by_key("1eQwoa3etxf3g82jZop50lt598NJRCZ2bHRUUMQDsSOw")
    sheet = spreadsheet.sheet1

    print("SPREADSHEET:", spreadsheet.title)
    print("WORKSHEET:", sheet.title)

    return sheet

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