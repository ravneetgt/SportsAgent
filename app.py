import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# CONFIG
# -----------------------------
SPREADSHEET_NAME = "Sports AI Content"

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
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict, scope
    )

    client = gspread.authorize(creds)

    return client.open(SPREADSHEET_NAME).sheet1


# -----------------------------
# LOAD DATA (WITH ROW INDEX)
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    sheet = get_sheet()

    raw = sheet.get_all_records()

    data = []

    for i, row in enumerate(raw):
        row["_row"] = i + 2  # actual row in Google Sheet
        data.append(row)

    return sheet, data


# -----------------------------
# UPDATE STATUS
# -----------------------------
def update_status(sheet, sheet_row, status):
    header = sheet.row_values(1)

    if COL_STATUS not in header:
        st.error("Status column missing")
        return

    col_index = header.index(COL_STATUS) + 1

    sheet.update_cell(sheet_row, col_index, status)


# -----------------------------
# UPDATE CAPTION
# -----------------------------
def update_caption(sheet, sheet_row, caption):
    header = sheet.row_values(1)

    if COL_CAPTION not in header:
        st.error("Caption column missing")
        return

    col_index = header.index(COL_CAPTION) + 1

    sheet.update_cell(sheet_row, col_index, caption)


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Sports Content Dashboard", layout="wide")

st.title("Sports Content Dashboard")

sheet, data = load_data()

if not data:
    st.warning("No data found")
    st.stop()


# -----------------------------
# FILTERS
# -----------------------------
statuses = sorted(list(set([str(r.get(COL_STATUS, "")).strip() for r in data])))
categories = sorted(list(set([str(r.get(COL_CATEGORY, "")).strip() for r in data])))

st.sidebar.header("Filters")

selected_status = st.sidebar.selectbox(
    "Status",
    ["ALL"] + statuses
)

selected_category = st.sidebar.selectbox(
    "Sport",
    ["ALL"] + categories
)

only_pending = st.sidebar.checkbox("Only show pending", value=False)


# -----------------------------
# FILTER LOGIC
# -----------------------------
filtered = data

if selected_status != "ALL":
    filtered = [
        r for r in filtered
        if str(r.get(COL_STATUS, "")).strip() == selected_status
    ]

if selected_category != "ALL":
    filtered = [
        r for r in filtered
        if str(r.get(COL_CATEGORY, "")).strip() == selected_category
    ]

if only_pending:
    filtered = [
        r for r in filtered
        if str(r.get(COL_STATUS, "")).strip() == "PENDING"
    ]

st.write(f"Showing {len(filtered)} posts")


# -----------------------------
# DISPLAY POSTS
# -----------------------------
for row in filtered:
    st.markdown("---")

    sheet_row = row["_row"]

    title = row.get(COL_TITLE, "")
    category = row.get(COL_CATEGORY, "")
    caption = row.get(COL_CAPTION, "")
    image_url = row.get(COL_IMAGE, "")
    status = row.get(COL_STATUS, "")

    st.subheader(title)

    col1, col2 = st.columns([2, 3])

    # IMAGE
    with col1:
        if image_url:
            try:
                st.image(image_url, use_container_width=True)
            except:
                st.write("Image not available")
        else:
            st.write("No image")

    # CONTENT
    with col2:
        st.write("Category:", category)
        st.write("Status:", status)

        edited_caption = st.text_area(
            "Caption",
            value=caption,
            height=120,
            key=f"caption_{sheet_row}"
        )

        # BUTTONS
        b1, b2, b3, b4 = st.columns(4)

        # SAVE CAPTION
        if b1.button("Save", key=f"save_{sheet_row}"):
            update_caption(sheet, sheet_row, edited_caption)
            st.success("Caption saved")
            st.rerun()

        # APPROVE
        if b2.button("Approve", key=f"approve_{sheet_row}"):
            update_status(sheet, sheet_row, "APPROVED")
            st.success("Approved")
            st.rerun()

        # REJECT
        if b3.button("Reject", key=f"reject_{sheet_row}"):
            update_status(sheet, sheet_row, "REJECTED")
            st.warning("Rejected")
            st.rerun()