from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os

WIDTH = 1080
HEIGHT = 1350

LOGO_PATH = "assets/logo.png"


def download_image(url):
    try:
        res = requests.get(url, timeout=10)
        return Image.open(BytesIO(res.content)).convert("RGB")
    except:
        return Image.new("RGB", (WIDTH, HEIGHT), "black")


def resize_crop(img):
    img = img.resize((WIDTH, HEIGHT))
    return img


def add_overlay(img):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 120))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def create_post(image_url, title, caption, filename):
    try:
        # -----------------------------
        # LOAD IMAGE
        # -----------------------------
        img = download_image(image_url)
        img = resize_crop(img)
        img = add_overlay(img)

        draw = ImageDraw.Draw(img)

        # -----------------------------
        # FONTS
        # -----------------------------
        try:
            title_font = ImageFont.truetype("Arial.ttf", 60)
            caption_font = ImageFont.truetype("Arial.ttf", 38)
            brand_font = ImageFont.truetype("Arial.ttf", 30)
        except:
            title_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()

        # -----------------------------
        # TEXT POSITION
        # -----------------------------
        x = 60
        y = HEIGHT - 400

        # TITLE (shortened)
        title_text = title.split("-")[0][:80]
        draw.text((x, y), title_text, fill="white", font=title_font)
        y += 80

        # CAPTION (3 lines)
        for line in caption.split("\n")[:3]:
            draw.text((x, y), line, fill="white", font=caption_font)
            y += 50

        # -----------------------------
        # LOGO (top-left)
        # -----------------------------
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((120, 120))
            logo.putalpha(120)
            img.paste(logo, (40, 40), logo)

        # -----------------------------
        # WORDMARK (top-right)
        # -----------------------------
        draw.text(
            (WIDTH - 260, 50),
            "GAMETRAIT",
            fill=(255, 255, 255),
            font=brand_font
        )

        # -----------------------------
        # SAVE
        # -----------------------------
        os.makedirs("posts", exist_ok=True)

        img = img.convert("RGB")
        img.save(filename, quality=95)

        print("Saved:", filename)

        return filename

    except Exception as e:
        print("create_post error:", e)
        return None


# test
if __name__ == "__main__":
    create_post(
        "https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg",
        "India beats Australia in thriller",
        "India held nerve under pressure\nExecution was precise\nAustralia fell short",
        "posts/test.jpg"
    )
