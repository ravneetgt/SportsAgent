from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import time
import os


# -----------------------------
# CONFIG
# -----------------------------
WIDTH = 1080
HEIGHT = 1350

LOGO_PATH = "assets/logo.png"  # your logo file


# -----------------------------
# HELPERS
# -----------------------------
def load_font(size):
    try:
        return ImageFont.truetype("Helvetica.ttf", size)
    except:
        return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()

    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def create_post(title, caption, image_url):
    try:
        # -----------------------------
        # LOAD IMAGE
        # -----------------------------
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        # resize + crop to fit
        img = img.resize((WIDTH, HEIGHT))

        # -----------------------------
        # DARK OVERLAY
        # -----------------------------
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
        img = Image.alpha_composite(img, overlay)

        # -----------------------------
        # DRAW SETUP
        # -----------------------------
        draw = ImageDraw.Draw(img)

        title_font = load_font(64)
        caption_font = load_font(40)
        brand_font = load_font(40)

        padding = 60
        max_width = WIDTH - (padding * 2)

        # -----------------------------
        # WRAP TEXT
        # -----------------------------
        title_lines = wrap_text(title, title_font, max_width, draw)
        caption_lines = wrap_text(caption, caption_font, max_width, draw)

        # -----------------------------
        # DRAW TITLE
        # -----------------------------
        y = HEIGHT - 500

        for line in title_lines:
            draw.text((padding, y), line, font=title_font, fill="white")
            y += 70

        y += 20

        # -----------------------------
        # DRAW CAPTION
        # -----------------------------
        for line in caption_lines:
            draw.text((padding, y), line, font=caption_font, fill=(230, 230, 230))
            y += 50

        # -----------------------------
        # LOGO (TOP LEFT)
        # -----------------------------
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((120, 120))

            # make watermark lighter
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            logo.putalpha(alpha)

            img.paste(logo, (40, 40), logo)

        # -----------------------------
        # WORDMARK (UNDER LOGO)
        # -----------------------------
        draw.text((40, 180), "GAMETRAIT", font=brand_font, fill=(255, 255, 255, 180))

        # -----------------------------
        # CONVERT TO RGB (FIX)
        # -----------------------------
        img = img.convert("RGB")

        # -----------------------------
        # SAVE
        # -----------------------------
        filename = f"posts/post_{int(time.time())}.jpg"

        os.makedirs("posts", exist_ok=True)

        img.save(filename, "JPEG", quality=95)

        print("Saved:", filename)

        return filename

    except Exception as e:
        print("ERROR create_post:", e)
        return None
