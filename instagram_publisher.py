import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_secret(name):
    if name in os.environ:
        return os.environ.get(name)
    if name in st.secrets:
        return st.secrets[name]
    return None

IG_ID = get_secret("IG_BUSINESS_ID")
ACCESS_TOKEN = get_secret("IG_ACCESS_TOKEN")


def create_container(image_url, caption):

    url = f"https://graph.facebook.com/v25.0/{IG_ID}/media"

    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    r = requests.post(url, data=payload)
    data = r.json()

    if "id" not in data:
        raise Exception(f"Container creation failed: {data}")

    return data["id"]


def publish_container(creation_id):

    url = f"https://graph.facebook.com/v25.0/{IG_ID}/media_publish"

    payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    r = requests.post(url, data=payload)
    data = r.json()

    if "id" not in data:
        raise Exception(f"Publish failed: {data}")

    return data["id"]


def publish_instagram(image_url, caption):
    print("IG_ID:", IG_ID)
    print("TOKEN exists:", ACCESS_TOKEN is not None)
    print("IMAGE URL:", image_url)

    creation_id = create_container(image_url, caption)

    post_id = publish_container(creation_id)

    return post_id  