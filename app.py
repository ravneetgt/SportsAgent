import streamlit as st
import os
from datetime import datetime, date

from create_post import create_post
from instagram_publisher import publish_instagram
from sheets_client import get_sheet

st.set_page_config(layout="wide")

# -----------------------------
# HEADER
# -----------------------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=60)

with col_title:
    st.markdown("<h2 style='margin-top:10px;'>GAMETRAIT</h2>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=30)
def load_data():
    sheet = get_sheet()
    data  = sheet.get_all_values()

    if len(data) < 2:
        return []

    headers = [h if h else f"col_{i}" for i, h in enumerate(data[0])]

    records = []
    for row in data[1:]:
        item = {h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)}
        records.append(item)

    return records


# -----------------------------
# UPDATE ROW
# -----------------------------
def update_sheet_row(index, caption, status):
    sheet      = get_sheet()
    row_number = index + 2

    sheet.update_cell(row_number, 4, caption)
    sheet.update_cell(row_number, 8, status)

    st.success(f"Updated row {row_number}")


# -----------------------------
# DATE HELPERS
# -----------------------------
def format_date(ts):
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d %b %Y • %I:%M %p")
    except Exception:
        return ""


def parse_timestamp(ts):
    try:
        return datetime.fromtimestamp(int(ts))
    except Exception:
        return None


# -----------------------------
# MAIN
# -----------------------------
data = load_data()

if not data:
    st.warning("No data found")
    st.stop()

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

status      = st.sidebar.selectbox("Status",       ["ALL", "PENDING", "POSTED", "REJECTED"])
type_filter = st.sidebar.selectbox("Content Type", ["ALL", "instagram", "article"])

valid_dates = [parse_timestamp(d.get("Date")) for d in data if parse_timestamp(d.get("Date"))]

if valid_dates:
    min_date = min(valid_dates).date()
    max_date = max(valid_dates).date()
else:
    min_date = max_date = date.today()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered_data = []

for row in data:
    if status      != "ALL" and row.get("Status") != status:
        continue
    if type_filter != "ALL" and row.get("Type")   != type_filter:
        continue

    row_dt = parse_timestamp(row.get("Date"))
    if row_dt and not (date_range[0] <= row_dt.date() <= date_range[1]):
        continue

    filtered_data.append(row)

# -----------------------------
# TABS
# -----------------------------
tab1, tab2 = st.tabs(["📱 Instagram Posts", "📰 Articles"])

# -----------------------------
# INSTAGRAM
# -----------------------------
with tab1:
    insta = [d for d in filtered_data if d.get("Type") == "instagram"]

    for idx, row in enumerate(insta[::-1]):
        real_index = len(insta) - idx - 1

        st.divider()

        col1, col2 = st.columns([1, 1])

        with col1:
            image_url = row.get("Image URL", "")
            if image_url.startswith("http"):
                st.image(image_url, use_container_width=True)

        with col2:
            st.subheader(row.get("Title", ""))
            st.write(f"**Status:** {row.get('Status')}")
            st.write(f"**Score:** {row.get('Score')}")
            st.write(f"**Date:** {format_date(row.get('Date'))}")

            caption = st.text_area(
                "Caption",
                value=row.get("Short Caption", ""),
                height=120,
                key=f"caption_{real_index}"
            )

            colA, colB, colC = st.columns(3)

            with colA:
                if st.button("Preview", key=f"preview_{real_index}"):
                    create_post(image_url, row.get("Title", ""), caption, "preview.jpg")
                    st.image("preview.jpg", use_container_width=True)

            with colB:
                if st.button("Approve & Post", key=f"approve_{real_index}"):
                    with st.spinner("Publishing to Instagram..."):
                        try:
                            post_id = publish_instagram(image_url, caption)
                            update_sheet_row(real_index, caption, "POSTED")
                            st.success("Instagram post published")
                            st.write("Post ID:", post_id)
                        except Exception as e:
                            st.error(f"Instagram publish failed: {e}")

            with colC:
                if st.button("Reject", key=f"reject_{real_index}"):
                    update_sheet_row(real_index, caption, "REJECTED")

# -----------------------------
# ARTICLES
# -----------------------------
with tab2:
    articles = [d for d in filtered_data if d.get("Type") == "article"]

    for row in articles[::-1]:
        st.divider()
        st.subheader(row.get("Title", ""))

        image_url = row.get("Image URL", "")
        if image_url.startswith("http"):
            st.image(image_url, use_container_width=True)

        st.write(f"**Status:** {row.get('Status')}")
        st.write(f"**Date:** {format_date(row.get('Date'))}")
        st.markdown("### Article")
        st.write(row.get("Article", ""))