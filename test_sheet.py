from push_to_sheet import get_sheet

sheet = get_sheet()
rows = sheet.get_all_values()

print("TOTAL ROWS:", len(rows))
print("LAST ROW:", rows[-1] if rows else None)