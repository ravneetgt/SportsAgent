import streamlit as st
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
SPREADSHEET_ID = "1ZEE3T6nj4_4wuE9XfCu6lMhunhhQnIn1F7w-vmF47mo"
WORKSHEET_NAME = "Sheet1"

st.set_page_config(layout="wide")

# -----------------------------
# AUTH (FIXED)
# -----------------------------
def get_creds():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # -------- CLOUD FIRST --------
    try:
        if "gcp_service_account" in st.secrets:
            print("Using STREAMLIT secrets")
            return ServiceAccountCredentials.from_json_keyfile_dict(
                st.secrets["gcp_service_account"], scope
            )
    except Exception as e:
        print("Secrets error:", e)

    # -------- LOCAL FALLBACK --------
    if os.path.exists("credentials.json"):
        print("Using LOCAL credentials.json")
        return ServiceAccountCredentials.from_json_keyfile_name(
            "credentials.json", scope
        )

    raise Exception("No credentials found")


def get_sheet():
    creds = get_creds()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
    return sheet


# -----------------------------
# LOAD DATA (FIXED)
# -----------------------------
@st.cache_data(ttl=30)
def load_data():
    try:
        sheet = get_sheet()
        data = sheet.get_all_values()

        if len(data) < 2:
            return []

        headers = data[0]

        # Fix empty headers
        headers = [h if h else f"col_{i}" for i, h in enumerate(headers)]

        rows = data[1:]

        records = []
        for row in rows:
            item = {}
            for i, h in enumerate(headers):
                item[h] = row[i] if i < len(row) else ""
            records.append(item)

        return records

    except Exception as e:
        st.error(f"Sheet error: {e}")
        return []


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


# -----------------------------
# DATE FORMAT
# -----------------------------
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
# SIDEBAR FILTERS
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
# TABS (KEY DIFFERENTIATION)
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
        for row in insta[::-1]:
            st.divider()

            col1, col2 = st.columns([1, 1])

            with col1:
                image_url = row.get("Image URL", "")

                if image_url.startswith("http"):
                    st.image(image_url, use_container_width=True)
                else:
                    st.warning("Invalid image")

            with col2:
                st.subheader(row.get("Title", ""))

                st.write(f"**Category:** {row.get('Category')}")
                st.write(f"**Status:** {row.get('Status')}")
                st.write(f"**Date:** {format_date(row.get('Date'))}")

                caption = st.text_area(
                    "Caption",
                    value=row.get("Short Caption", ""),
                    height=120
                )

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