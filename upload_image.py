"""
upload_image.py
---------------
Uploads a locally generated post image to cloud storage and returns
a permanent public URL. Required because Instagram's Graph API
needs a publicly accessible URL to create a media container.

PRIMARY:  Cloudinary  (recommended — free tier, reliable CDN)
FALLBACK: Imgur       (anonymous upload — no account needed but
                       images are public and may be removed over time)

Required environment variables
--------------------------------
Cloudinary path (set one of these):
  CLOUDINARY_URL        e.g. cloudinary://API_KEY:API_SECRET@CLOUD_NAME
  — OR all three separately:
  CLOUDINARY_CLOUD_NAME
  CLOUDINARY_API_KEY
  CLOUDINARY_API_SECRET

Imgur fallback (optional — only used if Cloudinary not configured):
  IMGUR_CLIENT_ID       anonymous client ID from https://api.imgur.com/oauth2/addclient

If neither is configured, raises UploadError.
"""

import os
import requests
import base64
from pathlib import Path


class UploadError(Exception):
    pass


# -----------------------------
# CLOUDINARY
# -----------------------------
def _cloudinary_config():
    """Returns (cloud_name, api_key, api_secret) or None."""
    url = os.getenv("CLOUDINARY_URL", "")
    if url.startswith("cloudinary://"):
        # Parse cloudinary://api_key:api_secret@cloud_name
        try:
            rest = url.replace("cloudinary://", "")
            credentials, cloud_name = rest.rsplit("@", 1)
            api_key, api_secret = credentials.split(":", 1)
            return cloud_name.strip(), api_key.strip(), api_secret.strip()
        except Exception:
            pass

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key    = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if cloud_name and api_key and api_secret:
        return cloud_name, api_key, api_secret

    return None


def _upload_cloudinary(file_path: str) -> str:
    config = _cloudinary_config()
    if not config:
        raise UploadError("Cloudinary not configured")

    cloud_name, api_key, api_secret = config

    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"

    with open(file_path, "rb") as f:
        files = {"file": f}
        data  = {
            "upload_preset": "ml_default",  # uses auto-create unsigned preset
            "folder": "gametrait",
        }

        # Signed upload if we have api_secret
        if api_secret:
            import hashlib, time as _time
            timestamp = int(_time.time())
            params    = f"folder=gametrait&timestamp={timestamp}"
            signature = hashlib.sha1(
                f"{params}{api_secret}".encode()
            ).hexdigest()

            data = {
                "api_key":   api_key,
                "timestamp": timestamp,
                "signature": signature,
                "folder":    "gametrait",
            }

            res = requests.post(
                upload_url,
                files=files,
                data=data,
                timeout=30
            )
        else:
            # Unsigned upload (requires an unsigned preset named "ml_default")
            res = requests.post(upload_url, files=files, data=data, timeout=30)

    if res.status_code != 200:
        raise UploadError(f"Cloudinary upload failed: {res.status_code} — {res.text[:200]}")

    result = res.json()
    secure_url = result.get("secure_url")

    if not secure_url:
        raise UploadError("Cloudinary returned no URL")

    return secure_url


# -----------------------------
# IMGUR (fallback)
# -----------------------------
def _upload_imgur(file_path: str) -> str:
    client_id = os.getenv("IMGUR_CLIENT_ID")
    if not client_id:
        raise UploadError("Imgur client ID not configured (IMGUR_CLIENT_ID)")

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    res = requests.post(
        "https://api.imgur.com/3/image",
        headers={"Authorization": f"Client-ID {client_id}"},
        data={"image": b64, "type": "base64"},
        timeout=30
    )

    if res.status_code != 200:
        raise UploadError(f"Imgur upload failed: {res.status_code} — {res.text[:200]}")

    result = res.json()
    link = result.get("data", {}).get("link")

    if not link:
        raise UploadError("Imgur returned no link")

    return link


# -----------------------------
# PUBLIC INTERFACE
# -----------------------------
def upload_image(file_path: str) -> str:
    """
    Upload file_path to cloud storage. Returns a public HTTPS URL.
    Tries Cloudinary first, falls back to Imgur.
    Raises UploadError if both fail.
    """
    if not os.path.exists(file_path):
        raise UploadError(f"File not found: {file_path}")

    # Try Cloudinary
    if _cloudinary_config():
        try:
            url = _upload_cloudinary(file_path)
            print(f"Uploaded via Cloudinary: {url}")
            return url
        except UploadError as e:
            print(f"Cloudinary failed, trying Imgur: {e}")

    # Try Imgur
    if os.getenv("IMGUR_CLIENT_ID"):
        try:
            url = _upload_imgur(file_path)
            print(f"Uploaded via Imgur: {url}")
            return url
        except UploadError as e:
            print(f"Imgur failed: {e}")

    raise UploadError(
        "Image upload failed. Configure CLOUDINARY_URL or IMGUR_CLIENT_ID."
    )
