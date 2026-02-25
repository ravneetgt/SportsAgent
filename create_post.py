from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

LOGO_PATH = "logo.png"
FONT_PATH = "Arial.ttf"


def create_post(image_url, title, caption, output_path):
    # -----------------------------
    # LOAD IMAGE FROM URL
    # -----------------------------
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")

    # Instagram square
    img = img.resize((1080, 1080))

    width, height = img.size

    # -----------------------------
    # GRADIENT OVERLAY (BOTTOM ONLY)
    # -----------------------------
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    for i in range(400):
        opacity = int(180 * (i / 400))
        overlay_draw.rectangle(
            [(0, height - i), (width, height - i + 1)],
            fill=(0, 0, 0, opacity)
        )

    img = Image.alpha_composite(img.convert('RGBA'), overlay)

    draw = ImageDraw.Draw(img)

    # -----------------------------
    # FONTS
    # -----------------------------
    try:
        title_font = ImageFont.truetype(FONT_PATH, 52)
        caption_font = ImageFont.truetype(FONT_PATH, 40)
        logo_font = ImageFont.truetype(FONT_PATH, 28)
    except:
        title_font = ImageFont.load_default()
        caption_font = ImageFont.load_default()
        logo_font = ImageFont.load_default()

    # -----------------------------
    # LOGO (TOP LEFT SMALL)
    # -----------------------------
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo.thumbnail((120, 120))
        img.paste(logo, (40, 40), logo)

        draw.text((170, 70), "GAMETRAIT", font=logo_font, fill="white")
    except:
        print("Logo not found")

    # -----------------------------
    # WRAP TEXT (IMPORTANT)
    # -----------------------------
    title_wrapped = textwrap.fill(title, width=28)
    caption_wrapped = textwrap.fill(caption, width=32)

    # -----------------------------
    # TITLE
    # -----------------------------
    draw.text(
        (60, height - 320),
        title_wrapped,
        font=title_font,
        fill=(255, 255, 255)
    )

    # -----------------------------
    # CAPTION
    # -----------------------------
    draw.text(
        (60, height - 160),
        caption_wrapped,
        font=caption_font,
        fill=(220, 220, 220)
    )

    # -----------------------------
    # SAVE
    # -----------------------------
    img = img.convert("RGB")
    img.save(output_path)

    return output_path