import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image


def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Sports AI Content").sheet1

    return sheet


def load_data():
    sheet = get_sheet()
    data = sheet.get_all_records()
    return sheet, data


st.title("Sports Content Dashboard")

sheet, data = load_data()

if not data:
    st.write("No posts found")
else:
    for i, row in enumerate(data):
        status = row.get("Status")

        # show only pending
        if status != "PENDING":
            continue

        st.markdown("---")

        title = row.get("Title")
        category = row.get("Category")
        caption = row.get("Caption")
        image_url = row.get("Image URL")

        st.subheader(title)
        st.write("Category:", category)

        # show image (URL or local path)
        try:
            if image_url.startswith("http"):
                st.image(image_url)
            else:
                img = Image.open(image_url)
                st.image(img)
        except:
            st.write("Image not available")

        st.text(caption)

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Approve {i}"):
                sheet.update_cell(i + 2, 5, "APPROVED")
                st.success("Approved!")

        with col2:
            if st.button(f"Reject {i}"):
                sheet.update_cell(i + 2, 5, "REJECTED")
                st.warning("Rejected!")
