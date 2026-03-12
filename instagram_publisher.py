import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# -----------------------------
# SECRET LOADER
# -----------------------------
def get_secret(name):

    # try environment variables first
    val = os.getenv(name)
    if val:
        return val

    # try streamlit secrets
    try:
        if name in st.secrets:
            return st.secrets[name]

        if "instagram" in st.secrets and name in st.secrets["instagram"]:
            return st.secrets["instagram"][name]
    except:
        pass

    return None


# -----------------------------
# CREATE MEDIA CONTAINER
# -----------------------------
def create_container(ig_id, token, image_url, caption):

    url = f"https://graph.facebook.com/v25.0/{ig_id}/media"

    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }

    r = requests.post(url, data=payload)
    data = r.json()

    if "id" not in data:
        raise Exception(f"Container creation failed: {data}")

    return data["id"]


# -----------------------------
# CHECK CONTAINER STATUS
# -----------------------------
def check_container_status(token, creation_id):

    url = f"https://graph.facebook.com/v25.0/{creation_id}"

    params = {
        "fields": "status_code",
        "access_token": token
    }

    r = requests.get(url, params=params)
    data = r.json()

    return data.get("status_code")


# -----------------------------
# WAIT UNTIL MEDIA READY
# -----------------------------
def wait_until_ready(token, creation_id):

    for _ in range(10):  # wait up to ~20 seconds

        status = check_container_status(token, creation_id)

        if status == "FINISHED":
            return True

        if status == "ERROR":
            raise Exception("Instagram container processing failed")

        time.sleep(2)

    raise Exception("Instagram media not ready after waiting")


# -----------------------------
# PUBLISH CONTAINER
# -----------------------------
def publish_container(ig_id, token, creation_id):

    url = f"https://graph.facebook.com/v25.0/{ig_id}/media_publish"

    payload = {
        "creation_id": creation_id,
        "access_token": token
    }

    r = requests.post(url, data=payload)
    data = r.json()

    if "id" not in data:
        raise Exception(f"Publish failed: {data}")

    return data["id"]


# -----------------------------
# MAIN PUBLISH FUNCTION
# -----------------------------
def publish_instagram(image_url, caption):

    IG_ID = get_secret("IG_BUSINESS_ID")
    ACCESS_TOKEN = get_secret("IG_ACCESS_TOKEN")

    if not IG_ID:
        raise Exception("IG_BUSINESS_ID missing")

    if not ACCESS_TOKEN:
        raise Exception("IG_ACCESS_TOKEN missing")

    # create container
    creation_id = create_container(
        IG_ID,
        ACCESS_TOKEN,
        image_url,
        caption
    )

    # wait for instagram processing
    wait_until_ready(
        ACCESS_TOKEN,
        creation_id
    )

    # publish
    post_id = publish_container(
        IG_ID,
        ACCESS_TOKEN,
        creation_id
    )

    return post_id