import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
SHEET_NAME = "Sports AI Content"

COL_CATEGORY = "Category"
COL_TITLE = "Title"
COL_CAPTION = "Caption"
COL_IMAGE = "Image URL"
COL_STATUS = "Status"
COL_DATE = "Date"


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

    return client.open(SHEET_NAME).sheet1


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=30)
def load_data():
    sheet = get_sheet()

    raw = sheet.get_all_records()

    data = []

    for i, row in enumerate(raw):
        row["_row"] = i + 2
        data.append(row)

    return data


# -----------------------------
# UPDATE STATUS
# -----------------------------
def update_status(sheet_row, status):
    try:
        sheet = get_sheet()

        header = sheet.row_values(1)

        col_index = header.index(COL_STATUS) + 1

        sheet.update_cell(sheet_row, col_index, status)

    except Exception as e:
        st.error(f"Update failed: {e}")


# -----------------------------
# UPDATE CAPTION
# -----------------------------
def update_caption(sheet_row, caption):
    try:
        sheet = get_sheet()

        header = sheet.row_values(1)

        col_index = header.index(COL_CAPTION) + 1

        sheet.update_cell(sheet_row, col_index, caption)

    except Exception as e:
        st.error(f"Caption update failed: {e}")


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title="Sports Dashboard", layout="wide")

st.title("Sports Content Dashboard")

if st.button("Refresh"):
    st.cache_data.clear()
    st.rerun()

data = load_data()

if not data:
    st.warning("No data")
    st.stop()


# -----------------------------
# PREP DATE
# -----------------------------
for row in data:
    if COL_DATE in row and row[COL_DATE]:
        try:
            row["_date_obj"] = datetime.strptime(row[COL_DATE], "%Y-%m-%d").date()
        except:
            row["_date_obj"] = None
    else:
        row["_date_obj"] = None


# -----------------------------
# FILTERS
# -----------------------------
statuses = sorted(list(set([str(r.get(COL_STATUS, "")) for r in data])))
categories = sorted(list(set([str(r.get(COL_CATEGORY, "")) for r in data])))

dates = sorted(list(set([r["_date_obj"] for r in data if r["_date_obj"]])))

st.sidebar.header("Filters")

selected_status = st.sidebar.selectbox("Status", ["ALL"] + statuses)
selected_category = st.sidebar.selectbox("Sport", ["ALL"] + categories)

selected_date = st.sidebar.selectbox(
    "Date",
    ["ALL"] + [str(d) for d in dates]
)

only_pending = st.sidebar.checkbox("Only Pending", value=False)


# -----------------------------
# FILTER LOGIC
# -----------------------------
filtered = data

if selected_status != "ALL":
    filtered = [r for r in filtered if str(r.get(COL_STATUS, "")) == selected_status]

if selected_category != "ALL":
    filtered = [r for r in filtered if str(r.get(COL_CATEGORY, "")) == selected_category]

if selected_date != "ALL":
    filtered = [
        r for r in filtered
        if r["_date_obj"] and str(r["_date_obj"]) == selected_date
    ]

if only_pending:
    filtered = [r for r in filtered if str(r.get(COL_STATUS, "")) == "PENDING"]

st.write(f"Showing {len(filtered)} posts")


# -----------------------------
# DISPLAY
# -----------------------------
for row in filtered:
    st.markdown("---")

    sheet_row = row["_row"]

    title = row.get(COL_TITLE, "")
    category = row.get(COL_CATEGORY, "")
    caption = row.get(COL_CAPTION, "")
    image_url = row.get(COL_IMAGE, "")
    status = row.get(COL_STATUS, "")
    date = row.get(COL_DATE, "")

    st.subheader(title)

    col1, col2 = st.columns([2, 3])

    with col1:
        if image_url:
            st.image(image_url, use_container_width=True)

    with col2:
        st.write("Category:", category)
        st.write("Status:", status)
        st.write("Date:", date)

        new_caption = st.text_area(
            "Caption",
            value=caption,
            height=120,
            key=f"caption_{sheet_row}"
        )

        b1, b2, b3, b4 = st.columns(4)

        if b1.button("Save", key=f"save_{sheet_row}"):
            update_caption(sheet_row, new_caption)
            st.success("Saved")
            st.rerun()

        if b2.button("Approve", key=f"approve_{sheet_row}"):
            update_status(sheet_row, "APPROVED")
            st.success("Approved")
            st.rerun()

        if b3.button("Reject", key=f"reject_{sheet_row}"):
            update_status(sheet_row, "REJECTED")
            st.warning("Rejected")
            st.rerun()

        if b4.button("Pending", key=f"pending_{sheet_row}"):
            update_status(sheet_row, "PENDING")
            st.info("Pending")
            st.rerun()
