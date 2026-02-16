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

    sheet = client.open(SPREADSHEET_NAME).sheet1

    return sheet


@st.cache_data(ttl=60)
def load_data():
    sheet = get_sheet()
    data = sheet.get_all_records()
    return sheet, data


def update_status(sheet, row_index, status):
    header = sheet.row_values(1)

    if COL_STATUS not in header:
        st.error("Status column missing")
        return

    col_index = header.index(COL_STATUS) + 1

    # +2 because sheet starts at row 1 and header is row 1
    sheet.update_cell(row_index + 2, col_index, status)


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
statuses = sorted(list(set([str(r.get(COL_STATUS, "")) for r in data])))
categories = sorted(list(set([str(r.get(COL_CATEGORY, "")) for r in data])))

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
        if str(r.get(COL_STATUS, "")) == selected_status
    ]

if selected_category != "ALL":
    filtered = [
        r for r in filtered
        if str(r.get(COL_CATEGORY, "")) == selected_category
    ]

if only_pending:
    filtered = [
        r for r in filtered
        if str(r.get(COL_STATUS, "")) == "PENDING"
    ]

st.write(f"Showing {len(filtered)} posts")

# -----------------------------
# DISPLAY POSTS
# -----------------------------
for i, row in enumerate(filtered):
    st.markdown("---")

    title = row.get(COL_TITLE)
    category = row.get(COL_CATEGORY)
    caption = row.get(COL_CAPTION)
    image_url = row.get(COL_IMAGE)
    status = row.get(COL_STATUS)

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

        st.text_area(
            "Caption",
            value=caption,
            height=120,
            key=f"caption_{i}"
        )

        b1, b2, b3 = st.columns(3)

        if b1.button("Approve", key=f"approve_{i}"):
            update_status(sheet, i, "APPROVED")
            st.success("Approved")
            st.rerun()

        if b2.button("Reject", key=f"reject_{i}"):
            update_status(sheet, i, "REJECTED")
            st.warning("Rejected")
            st.rerun()

        if b3.button("Pending", key=f"pending_{i}"):
            update_status(sheet, i, "PENDING")
            st.info("Set to pending")
            st.rerun()
