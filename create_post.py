from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import os


# -----------------------------
# CONFIG
# -----------------------------
WIDTH = 1080
HEIGHT = 1350

LOGO_PATH = "assets/logo.png"  # your logo file

FONT_PATH = "/System/Library/Fonts/Supplemental/Helvetica.ttf"


# -----------------------------
# HELPERS
# -----------------------------
def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()

    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def create_post(image_url, title, caption, output_path):
    try:
        # -----------------------------
        # DOWNLOAD IMAGE
        # -----------------------------
        res = requests.get(image_url, timeout=10)
        base = Image.open(BytesIO(res.content)).convert("RGB")

        # -----------------------------
        # RESIZE + CROP (CENTER)
        # -----------------------------
        base_ratio = base.width / base.height
        target_ratio = WIDTH / HEIGHT

        if base_ratio > target_ratio:
            # crop width
            new_width = int(base.height * target_ratio)
            left = (base.width - new_width) // 2
            base = base.crop((left, 0, left + new_width, base.height))
        else:
            # crop height
            new_height = int(base.width / target_ratio)
            top = (base.height - new_height) // 2
            base = base.crop((0, top, base.width, top + new_height))

        base = base.resize((WIDTH, HEIGHT))

        # -----------------------------
        # DARK OVERLAY (FIXED)
        # -----------------------------
        base = base.convert("RGBA")

        # Light overall darkening
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 70))
        base = Image.alpha_composite(base, overlay)

        # -----------------------------
        # GRADIENT (bottom dark for text)
        # -----------------------------
        gradient = Image.new("L", (1, HEIGHT), 0)

        for y in range(HEIGHT):
            if y > HEIGHT * 0.55:
                opacity = int(255 * ((y - HEIGHT * 0.55) / (HEIGHT * 0.45)))
                gradient.putpixel((0, y), min(opacity, 255))
            else:
                gradient.putpixel((0, y), 0)

        alpha_gradient = gradient.resize((WIDTH, HEIGHT))

        black_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 200))

        base = Image.composite(black_overlay, base, alpha_gradient)

        # -----------------------------
        # DRAW CONTEXT (AFTER overlay)
        # -----------------------------
        draw = ImageDraw.Draw(base)


        # -----------------------------
        # FONTS (BIG + READABLE)
        # -----------------------------
       # FONTS
        title_font = load_font(90)
        caption_font = load_font(48)

        # LAYOUT CONFIG
        margin = 60
        max_width = WIDTH - (margin * 2)

        # WRAP TEXT
        title_lines = wrap_text(title, title_font, max_width, draw)
        caption_lines = wrap_text(caption, caption_font, max_width, draw)

        # -----------------------------
        # WRAP TEXT
        # -----------------------------
        title_lines = wrap_text(title, title_font, max_width, draw)
        caption_lines = wrap_text(caption, caption_font, max_width, draw)

        # -----------------------------
        # POSITIONING
        # -----------------------------
        y = HEIGHT * 0.45  # start lower half

        # TITLE
        for line in title_lines:
            draw.text((margin, y), line, font=title_font, fill="white")
            y += title_font.size + 12

        y += 20

        # CAPTION
        for line in caption_lines:
            draw.text((margin, y), line, font=caption_font, fill="white")
            y += caption_font.size + 10

        # -----------------------------
        # LOGO TOP LEFT
        # -----------------------------
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = logo.resize((120, 120))

            base.paste(logo, (40, 40), logo)

            # WORDMARK BELOW LOGO
            wordmark_font = load_font(40)
            draw.text((40, 170), "GAMETRAIT", font=wordmark_font, fill="white")

        # -----------------------------
        # SAVE
        # -----------------------------
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        base = base.convert("RGB")  # FIX JPEG ERROR

        base.save(output_path, "JPEG", quality=95)

        print("Saved:", output_path)
        return output_path

    except Exception as e:
        print("create_post ERROR:", e)
        return None
