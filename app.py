import streamlit as st
import os
from datetime import datetime, date

from create_post import create_post
from instagram_publisher import publish_instagram
from sheets_client import get_sheet

st.set_page_config(layout="wide")

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

col_logo, col_title = st.columns([1,6])

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=60)

with col_title:
    st.markdown("<h2 style='margin-top:10px;'>GAMETRAIT</h2>", unsafe_allow_html=True)

st.markdown("---")


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data(ttl=30)
def load_data():

    sheet = get_sheet()

    data = sheet.get_all_values()

    if len(data) < 2:
        return []

    headers = data[0]

    rows = []

    for i, row in enumerate(data[1:]):

        item = {h:(row[j] if j < len(row) else "") for j,h in enumerate(headers)}

        item["_row"] = i + 2

        rows.append(item)

    return rows


# ---------------------------------------------------
# UPDATE ROW
# ---------------------------------------------------

def update_sheet_row(row_number, caption, status):

    sheet = get_sheet()

    sheet.update_cell(row_number, 7, caption)
    sheet.update_cell(row_number, 11, status)

    st.success(f"Updated row {row_number}")


# ---------------------------------------------------
# APPROVE MATCHING ARTICLE
# ---------------------------------------------------

def approve_matching_article(title):

    sheet = get_sheet()

    rows = sheet.get_all_values()

    headers = rows[0]

    type_idx = headers.index("Type")
    title_idx = headers.index("Title")
    status_idx = headers.index("Status")

    for i,row in enumerate(rows[1:], start=2):

        if len(row) <= title_idx:
            continue

        if row[type_idx] == "article" and row[title_idx] == title:

            sheet.update_cell(i, status_idx+1, "Approved")


# ---------------------------------------------------
# DATE HELPERS
# ---------------------------------------------------

def format_date(ts):

    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d %b %Y • %I:%M %p")
    except:
        return ""


def parse_timestamp(ts):

    try:
        return datetime.fromtimestamp(int(ts))
    except:
        return None


# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

data = load_data()

if not data:
    st.warning("No data found")
    st.stop()


# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("Filters")

status = st.sidebar.selectbox("Status",["ALL","PENDING","POSTED","REJECTED"])

type_filter = st.sidebar.selectbox("Content Type",["ALL","instagram","article"])


# NEW FILTERS
league_filter = st.sidebar.text_input("League")

team_filter = st.sidebar.text_input("Team")

player_filter = st.sidebar.text_input("Player")

category_filter = st.sidebar.text_input("Category")


valid_dates = [parse_timestamp(d.get("Date")) for d in data if parse_timestamp(d.get("Date"))]

if valid_dates:

    min_date = min(valid_dates).date()

    max_date = max(valid_dates).date()

else:

    min_date = max_date = date.today()


date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date,max_date),
    min_value=min_date,
    max_value=max_date
)


# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered_data = []

for row in data:

    if status != "ALL" and row.get("Status") != status:
        continue

    if type_filter != "ALL" and row.get("Type") != type_filter:
        continue

    if league_filter and league_filter.lower() not in row.get("League","").lower():
        continue

    if team_filter and team_filter.lower() not in row.get("Team","").lower():
        continue

    if player_filter and player_filter.lower() not in row.get("Player","").lower():
        continue

    if category_filter and category_filter.lower() not in row.get("Category","").lower():
        continue

    row_dt = parse_timestamp(row.get("Date"))

    if row_dt and not (date_range[0] <= row_dt.date() <= date_range[1]):
        continue

    filtered_data.append(row)


# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2 = st.tabs(["📱 Instagram Posts","📰 Articles"])


# ---------------------------------------------------
# INSTAGRAM
# ---------------------------------------------------

with tab1:

    insta = [d for d in filtered_data if d.get("Type") == "instagram"]

    for row in insta[::-1]:

        st.divider()

        row_number = row["_row"]

        col1,col2 = st.columns([1,1])

        with col1:

            image_url = row.get("Image URL","")

            if image_url.startswith("http"):
                st.image(image_url, use_container_width=True)

        with col2:

            st.subheader(row.get("Title",""))

            # NEW FIELDS
            st.write("**League:**", row.get("League",""))
            st.write("**Team:**", row.get("Team",""))
            st.write("**Player:**", row.get("Player",""))
            st.write("**Category:**", row.get("Category",""))

            st.write("**Status:**", row.get("Status"))
            st.write("**Score:**", row.get("Score"))
            st.write("**Date:**", format_date(row.get("Date")))

            caption = st.text_area(
                "Caption",
                value=row.get("Short Caption",""),
                height=120,
                key=f"caption_{row_number}"
            )

            colA,colB,colC = st.columns(3)


            # PREVIEW
            with colA:

                if st.button("Preview", key=f"preview_{row_number}"):

                    create_post(image_url,row.get("Title",""),caption,"preview.jpg")

                    st.image("preview.jpg",use_container_width=True)


            # APPROVE
            with colB:

                if st.button("Approve & Post", key=f"approve_{row_number}"):

                    with st.spinner("Publishing to Instagram..."):

                        try:

                            post_id = publish_instagram(image_url,caption)

                            update_sheet_row(row_number,caption,"POSTED")

                            approve_matching_article(row.get("Title"))

                            st.success("Instagram post published")

                            st.write("Post ID:",post_id)

                        except Exception as e:

                            st.error(f"Instagram publish failed: {e}")


            # REJECT
            with colC:

                if st.button("Reject", key=f"reject_{row_number}"):

                    update_sheet_row(row_number,caption,"REJECTED")


# ---------------------------------------------------
# ARTICLES
# ---------------------------------------------------

with tab2:

    articles = [d for d in filtered_data if d.get("Type") == "article"]

    for row in articles[::-1]:

        st.divider()

        st.subheader(row.get("Title",""))

        image_url = row.get("Image URL","")

        if image_url.startswith("http"):
            st.image(image_url,use_container_width=True)

        # NEW FIELDS
        st.write("**League:**", row.get("League",""))
        st.write("**Team:**", row.get("Team",""))
        st.write("**Player:**", row.get("Player",""))
        st.write("**Category:**", row.get("Category",""))

        st.write("**Status:**", row.get("Status"))

        st.write("**Date:**", format_date(row.get("Date")))

        st.markdown("### Article")

        st.write(row.get("Article",""))