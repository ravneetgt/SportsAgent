import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# CONFIG
# -----------------------------
SPREADSHEET_NAME = "Sports AI Content"
SHEET_NAME = None  # None = first sheet

# Column names (must match your Google Sheet headers exactly)
COL_CATEGORY = "Category"
COL_TITLE = "Title"
COL_CAPTION = "Caption"
COL_IMAGE = "Image URL"
COL_STATUS = "Status"

# -----------------------------
# GOOGLE SHEETS
# -----------------------------
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # read credentials from Streamlit secrets
    creds_dict = dict(st.secrets["gcp_service_account"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    if SHEET_NAME:
        sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    else:
        sheet = client.open(SPREADSHEET_NAME).sheet1

    return sheet


@st.cache_data(ttl=60)
def load_data():
    sheet = get_sheet()
    records = sheet.get_all_records()  # list of dicts
    return sheet, records


def update_status(sheet, row_index, status_value):
    # gspread rows are 1-indexed, and row 1 is header
    # so data row i -> sheet row = i + 2
    header = sheet.row_values(1)

    if COL_STATUS not in header:
        st.error(f"Column '{COL_STATUS}' not found in sheet.")
        return

    col_idx = header.index(COL_STATUS) + 1
    sheet.update_cell(row_index + 2, col_idx, status_value)


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Sports Agent", layout="wide")

st.title("Sports Content Review")

sheet, data = load_data()

if not data:
    st.warning("No data found in sheet.")
    st.stop()

st.write(f"Total items: {len(data)}")

# Filter by status
statuses = sorted(list(set([str(r.get(COL_STATUS, "")) for r in data])))
selected_status = st.selectbox(
    "Filter by status", ["ALL"] + statuses, index=0
)

filtered = data
if selected_status != "ALL":
    filtered = [r for r in data if str(r.get(COL_STATUS, "")) == selected_status]

# -----------------------------
# DISPLAY ITEMS
# -----------------------------
for idx, row in enumerate(filtered):
    st.markdown("---")

    category = row.get(COL_CATEGORY, "")
    title = row.get(COL_TITLE, "")
    caption = row.get(COL_CAPTION, "")
    image_url = row.get(COL_IMAGE, "")
    status = row.get(COL_STATUS, "")

    st.subheader(title)

    cols = st.columns([2, 3])

    # IMAGE
    with cols[0]:
        if image_url:
            try:
                st.image(image_url, use_container_width=True)
            except Exception:
                st.write("Image failed to load")
        else:
            st.write("No image")

    # CONTENT
    with cols[1]:
        st.write("Category:", category)
        st.write("Status:", status)

        st.text_area(
            "Caption",
            value=caption,
            height=120,
            key=f"caption_{idx}",
        )

        btn_cols = st.columns(3)

        if btn_cols[0].button("Approve", key=f"approve_{idx}"):
            update_status(sheet, idx, "APPROVED")
            st.success("Approved")
            st.experimental_rerun()

        if btn_cols[1].button("Reject", key=f"reject_{idx}"):
            update_status(sheet, idx, "REJECTED")
            st.warning("Rejected")
            st.experimental_rerun()

        if btn_cols[2].button("Pending", key=f"pending_{idx}"):
            update_status(sheet, idx, "PENDING")
            st.info("Marked pending")
            st.experimental_rerun()
