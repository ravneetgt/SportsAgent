import os
import requests
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1350  # Instagram 4:5

LOGO_PATH = "assets/logo.png"
FONT_PATH = "Arial.ttf"


# -----------------------------
# LOAD IMAGE
# -----------------------------
def load_image(source):
    try:
        if source.startswith("http"):
            res = requests.get(source, timeout=10)
            return Image.open(BytesIO(res.content)).convert("RGB")
        else:
            return Image.open(source).convert("RGB")
    except:
        return Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))


# -----------------------------
# RESIZE COVER
# -----------------------------
def resize_cover(img):
    img_ratio = img.width / img.height
    target_ratio = WIDTH / HEIGHT

    if img_ratio > target_ratio:
        new_height = HEIGHT
        new_width = int(new_height * img_ratio)
    else:
        new_width = WIDTH
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height))

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return img.crop((left, top, left + WIDTH, top + HEIGHT))


# -----------------------------
# GRADIENT
# -----------------------------
def add_gradient(img):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for i in range(700):
        opacity = int(200 * (i / 700))
        draw.rectangle(
            [(0, HEIGHT - i), (WIDTH, HEIGHT - i + 1)],
            fill=(0, 0, 0, opacity),
        )

    return Image.alpha_composite(img.convert("RGBA"), overlay)


# -----------------------------
# TEXT DRAW
# -----------------------------
def draw_text(draw, text, font, x, y, width, color):
    lines = textwrap.wrap(text, width=width)

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill=color,
            stroke_width=2,
            stroke_fill=(0, 0, 0),
        )
        y += font.getbbox(line)[3] + 8

    return y


# -----------------------------
# MAIN
# -----------------------------
def create_post(image_source, title, overlay_text, output_path="preview.png"):

    img = load_image(image_source)
    img = resize_cover(img)
    img = add_gradient(img)

    draw = ImageDraw.Draw(img)

    # FONTS
    try:
        title_font = ImageFont.truetype(FONT_PATH, 60)
        caption_font = ImageFont.truetype(FONT_PATH, 42)
        brand_font = ImageFont.truetype(FONT_PATH, 30)
    except:
        title_font = ImageFont.load_default()
        caption_font = ImageFont.load_default()
        brand_font = ImageFont.load_default()

    # -----------------------------
    # BRANDING (TOP LEFT)
    # -----------------------------
    try:
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo.thumbnail((80, 80))

            img.paste(logo, (40, 40), logo)

            draw.text(
                (140, 55),
                "GAMETRAIT",
                font=brand_font,
                fill=(255, 255, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0),
            )
        else:
            draw.text((40, 50), "GAMETRAIT", font=brand_font, fill=(255, 255, 255))
    except Exception as e:
        print("Logo error:", e)

    # -----------------------------
    # TITLE
    # -----------------------------
    y = HEIGHT - 420
    y = draw_text(draw, title, title_font, 60, y, 28, (255, 255, 255))

    # -----------------------------
    # OVERLAY CAPTION
    # -----------------------------
    overlay_text = overlay_text[:180]

    draw_text(draw, overlay_text, caption_font, 60, y + 20, 34, (220, 220, 220))

    # SAVE
    img = img.convert("RGB")
    img.save(output_path)

    return output_path