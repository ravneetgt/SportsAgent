import os
import requests

IG_ID = os.getenv("IG_BUSINESS_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")


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

    creation_id = create_container(image_url, caption)

    post_id = publish_container(creation_id)

    return post_id