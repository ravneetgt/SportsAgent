import time
from sheets_client import get_sheet


def push_if_new(row):
    try:
        sheet = get_sheet()

        # -----------------------------
        # DEDUPE
        # -----------------------------
        existing = sheet.get_all_records()

        for r in existing:
            if (
                r.get("Title") == row.get("Title")
                and r.get("Type") == row.get("Type")
            ):
                print("SKIP:", row.get("Title")[:60], row.get("Type"))
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

        print("ADDING:", row.get("Title")[:60], row.get("Type"))

        sheet.append_row(values, table_range="A1:K1")

        print("ADDED SUCCESSFULLY")

        return True

    except Exception as e:
        print("Sheet push error:", str(e))
        return False
