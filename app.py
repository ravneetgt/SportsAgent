import streamlit as st
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from create_post import create_post  # ✅ NEW

# -----------------------------
# CONFIG
# -----------------------------
SPREADSHEET_ID = "1eQwoa3etxf3g82jZop50lt598NJRCZ2bHRUUMQDsSOw"
WORKSHEET_NAME = "Sheet1"

st.set_page_config(layout="wide")

# -----------------------------
# AUTH
# -----------------------------
def get_creds():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    try:
        if "gcp_service_account" in st.secrets:
            return ServiceAccountCredentials.from_json_keyfile_dict(
                st.secrets["gcp_service_account"], scope
            )
    except Exception as e:
        print("Secrets error:", e)

    if os.path.exists("credentials.json"):
        return ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )

    raise Exception("No credentials found")


def get_sheet():
    creds = get_creds()
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=30)
def load_data():
    sheet = get_sheet()
    data = sheet.get_all_values()

    if len(data) < 2:
        return []

    headers = [h if h else f"col_{i}" for i, h in enumerate(data[0])]
    rows = data[1:]

    records = []
    for row in rows:
        item = {}
        for i, h in enumerate(headers):
            item[h] = row[i] if i < len(row) else ""
        records.append(item)

    return records


# -----------------------------
# UPDATE STATUS (NEW)
# -----------------------------
def update_sheet_row(index, caption, status):
    sheet = get_sheet()

    # +2 because sheet is 1-indexed and header row exists
    row_number = index + 2

    # Short Caption = column 4 (0-based index 3)
    # Status = column 8 (0-based index 7)
    sheet.update_cell(row_number, 4, caption)
    sheet.update_cell(row_number, 8, status)

    st.success(f"Updated row {row_number}")


# -----------------------------
# FILTERS
# -----------------------------
def apply_filters(data, status, category, type_filter):
    filtered = []

    for row in data:
        if status != "ALL" and row.get("Status") != status:
            continue

        if category != "ALL" and row.get("Category") != category:
            continue

        if type_filter != "ALL" and row.get("Type") != type_filter:
            continue

        filtered.append(row)

    return filtered


def format_date(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d %b %Y, %I:%M %p")
    except:
        return ""


# -----------------------------
# UI
# -----------------------------
st.title("Gametrait Sports Content Dashboard")

data = load_data()

if not data:
    st.warning("No data found")
    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Filters")

status = st.sidebar.selectbox(
    "Status",
    ["ALL", "PENDING", "APPROVED", "REJECTED"]
)

category = st.sidebar.selectbox(
    "Sport",
    ["ALL"] + sorted(list(set([d.get("Category", "") for d in data])))
)

type_filter = st.sidebar.selectbox(
    "Content Type",
    ["ALL", "instagram", "article"]
)

filtered_data = apply_filters(data, status, category, type_filter)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["📱 Instagram Posts", "📰 Articles"])

# -----------------------------
# INSTAGRAM TAB
# -----------------------------
with tab1:
    insta = [d for d in filtered_data if d.get("Type") == "instagram"]

    if not insta:
        st.info("No Instagram posts")
    else:
        for i, row in enumerate(insta[::-1]):
            st.divider()

            col1, col2 = st.columns([1, 1])

            # IMAGE
            with col1:
                image_url = row.get("Image URL", "")

                if image_url.startswith("http"):
                    st.image(image_url, use_container_width=True)
                else:
                    st.warning("Invalid image")

            # CONTENT
            with col2:
                st.subheader(row.get("Title", ""))

                st.write(f"**Category:** {row.get('Category')}")
                st.write(f"**Status:** {row.get('Status')}")
                st.write(f"**Date:** {format_date(row.get('Date'))}")

                # ✅ FIX: UNIQUE KEY
                caption = st.text_area(
                    "Caption",
                    value=row.get("Short Caption", ""),
                    height=120,
                    key=f"caption_{i}"
                )

                colA, colB, colC = st.columns(3)

                # PREVIEW
                with colA:
                    if st.button("Preview", key=f"preview_{i}"):
                        try:
                            post_path = create_post(
                                row["Image URL"],
                                row.get("Title", ""),
                                caption,
                                f"post_{i}.png"
                            )
                            st.image(post_path, use_container_width=True)
                        except Exception as e:
                            st.error(e)

                # APPROVE
                with colB:
                    if st.button("Approve", key=f"approve_{i}"):
                        update_sheet_row(i, caption, "APPROVED")

                # REJECT
                with colC:
                    if st.button("Reject", key=f"reject_{i}"):
                        update_sheet_row(i, caption, "REJECTED")


# -----------------------------
# ARTICLES TAB
# -----------------------------
with tab2:
    articles = [d for d in filtered_data if d.get("Type") == "article"]

    if not articles:
        st.info("No articles")
    else:
        for row in articles[::-1]:
            st.divider()

            st.subheader(row.get("Title", ""))

            image_url = row.get("Image URL", "")

            if image_url.startswith("http"):
                st.image(image_url, use_container_width=True)

            st.write(f"**Category:** {row.get('Category')}")
            st.write(f"**Status:** {row.get('Status')}")
            st.write(f"**Date:** {format_date(row.get('Date'))}")

            st.markdown("### Article")
            st.write(row.get("Article", ""))