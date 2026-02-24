import streamlit as st
import pandas as pd
from push_to_sheet import get_sheet

# -----------------------------
# CONFIG
# -----------------------------
HEADERS = [
    "Type",
    "Category",
    "Title",
    "Short Caption",
    "Long Caption",
    "Article",
    "Image URL",
    "Status",
    "Context",
    "Score",
    "Date"
]

# -----------------------------
# HELPERS
# -----------------------------
def is_valid_url(url):
    return isinstance(url, str) and url.startswith("http")


def safe_load_sheet():
    try:
        sheet = get_sheet()
        values = sheet.get_all_values()

        if not values or len(values) < 2:
            return pd.DataFrame(columns=HEADERS)

        header = values[0]
        data = values[1:]

        df = pd.DataFrame(data, columns=header)

        # Ensure all columns exist
        for col in HEADERS:
            if col not in df.columns:
                df[col] = ""

        return df

    except Exception as e:
        st.error(f"Sheet error: {str(e)}")
        return pd.DataFrame(columns=HEADERS)


@st.cache_data(ttl=30)
def load_data():
    df = safe_load_sheet()

    if df.empty:
        return df

    # Convert date safely
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


def update_status(row_idx, status):
    sheet = get_sheet()
    sheet.update_cell(row_idx, 8, status)  # Status column


def update_caption(row_idx, caption):
    sheet = get_sheet()
    sheet.update_cell(row_idx, 4, caption)  # Short Caption


# -----------------------------
# UI CONFIG
# -----------------------------
st.set_page_config(layout="wide")
st.title("Gametrait Sports Content Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
df = load_data()

if df.empty:
    st.warning("No data found")
    st.stop()

# Add row index (important for updates)
df["_row"] = df.index + 2  # offset header

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
with st.sidebar:
    st.header("Filters")

    status_filter = st.selectbox(
        "Status",
        ["ALL"] + sorted(df["Status"].dropna().unique().tolist())
    )

    category_filter = st.selectbox(
        "Sport",
        ["ALL"] + sorted(df["Category"].dropna().unique().tolist())
    )

    type_filter = st.selectbox(
        "Type",
        ["ALL"] + sorted(df["Type"].dropna().unique().tolist())
    )

    only_pending = st.checkbox("Only Pending")

# -----------------------------
# APPLY FILTERS
# -----------------------------
filtered = df.copy()

if status_filter != "ALL":
    filtered = filtered[filtered["Status"] == status_filter]

if category_filter != "ALL":
    filtered = filtered[filtered["Category"] == category_filter]

if type_filter != "ALL":
    filtered = filtered[filtered["Type"] == type_filter]

if only_pending:
    filtered = filtered[filtered["Status"] == "PENDING"]

# Sort newest first
if "Date" in filtered.columns:
    filtered = filtered.sort_values(by="Date", ascending=False)

# -----------------------------
# DISPLAY
# -----------------------------
for i, row in filtered.iterrows():

    st.divider()

    row_idx = int(row["_row"])
    content_type = row.get("Type", "")

    # -----------------------------
    # INSTAGRAM POSTS
    # -----------------------------
    if content_type == "instagram":

        col1, col2 = st.columns([1, 1])

        with col1:
            if is_valid_url(row.get("Image URL")):
                st.image(row["Image URL"], use_container_width=True)
            else:
                st.warning("No image")

        with col2:
            st.subheader(row.get("Title", ""))

            st.caption(
                f"POST | {row.get('Category')} | {row.get('Status')}"
            )

            st.markdown("### Caption")

            caption = st.text_area(
                "Edit Caption",
                value=row.get("Short Caption", ""),
                key=f"caption_{i}"
            )

            colA, colB, colC, colD = st.columns(4)

            with colA:
                if st.button("Save", key=f"save_{i}"):
                    update_caption(row_idx, caption)
                    st.success("Saved")

            with colB:
                if st.button("Approve", key=f"approve_{i}"):
                    update_status(row_idx, "APPROVED")
                    st.success("Approved")

            with colC:
                if st.button("Reject", key=f"reject_{i}"):
                    update_status(row_idx, "REJECTED")
                    st.success("Rejected")

            with colD:
                if st.button("Pending", key=f"pending_{i}"):
                    update_status(row_idx, "PENDING")
                    st.success("Pending")

    # -----------------------------
    # ARTICLES
    # -----------------------------
    elif content_type == "article":

        st.subheader(row.get("Title", ""))

        if is_valid_url(row.get("Image URL")):
            st.image(row["Image URL"], use_container_width=True)

        st.caption(
            f"ARTICLE | {row.get('Category')} | {row.get('Status')}"
        )

        st.markdown("### Article")
        st.write(row.get("Article", ""))

        st.markdown("### Summary")
        st.write(row.get("Long Caption", ""))

        colA, colB, colC = st.columns(3)

        with colA:
            if st.button("Approve", key=f"approve_a_{i}"):
                update_status(row_idx, "APPROVED")
                st.success("Approved")

        with colB:
            if st.button("Reject", key=f"reject_a_{i}"):
                update_status(row_idx, "REJECTED")
                st.success("Rejected")

        with colC:
            if st.button("Pending", key=f"pending_a_{i}"):
                update_status(row_idx, "PENDING")
                st.success("Pending")

    # -----------------------------
    # FALLBACK
    # -----------------------------
    else:
        st.write(row.to_dict())

# -----------------------------
# FOOTER
# -----------------------------
st.caption(f"{len(filtered)} items shown")