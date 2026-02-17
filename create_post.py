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

PADDING = 80
LINE_SPACING = 10

LOGO_PATH = "assets/logo.png"  # put your logo here


# -----------------------------
# LOAD IMAGE
# -----------------------------
def load_image(url):
    try:
        res = requests.get(url)
        img = Image.open(BytesIO(res.content)).convert("RGB")
        return img
    except:
        return Image.new("RGB", (WIDTH, HEIGHT), "black")


# -----------------------------
# RESIZE + CROP
# -----------------------------
def resize_image(img):
    img_ratio = img.width / img.height
    target_ratio = WIDTH / HEIGHT

    if img_ratio > target_ratio:
        # crop width
        new_height = HEIGHT
        new_width = int(new_height * img_ratio)
    else:
        # crop height
        new_width = WIDTH
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height))

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return img.crop((left, top, left + WIDTH, top + HEIGHT))


# -----------------------------
# GRADIENT OVERLAY
# -----------------------------
def add_gradient(img):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bottom dark gradient
    for i in range(HEIGHT):
        opacity = int(180 * (i / HEIGHT))
        draw.line((0, HEIGHT - i, WIDTH, HEIGHT - i), fill=(0, 0, 0, opacity))

    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    return img


# -----------------------------
# LOAD FONTS
# -----------------------------
def load_fonts():
    try:
        title_font = ImageFont.truetype("Helvetica.ttf", 64)
        body_font = ImageFont.truetype("Helvetica.ttf", 36)
        small_font = ImageFont.truetype("Helvetica.ttf", 28)
    except:
        # fallback if Helvetica not available
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    return title_font, body_font, small_font


# -----------------------------
# DRAW TEXT
# -----------------------------
def draw_caption(draw, caption, fonts):
    title_font, body_font, _ = fonts

    lines = caption.strip().split("\n")

    # Wrap each line properly
    wrapped_lines = []
    for line in lines:
        wrapped_lines.extend(textwrap.wrap(line, width=30))

    # Start from bottom
    y = HEIGHT - 400

    for i, line in enumerate(wrapped_lines):
        font = title_font if i == 0 else body_font

        draw.text(
            (PADDING, y),
            line,
            font=font,
            fill=(255, 255, 255)
        )

        y += font.size + LINE_SPACING


# -----------------------------
# LOGO (TOP LEFT)
# -----------------------------
def add_logo(img):
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")

        # Resize logo
        logo = logo.resize((120, 120))

        # Make it semi-transparent
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: p * 0.6)
        logo.putalpha(alpha)

        img.paste(logo, (40, 40), logo)

    except Exception as e:
        print("Logo error:", e)

    return img


# -----------------------------
# WORDMARK (TOP RIGHT)
# -----------------------------
def add_wordmark(draw, fonts):
    _, _, small_font = fonts

    text = "GAMETRAIT"

    w, h = draw.textsize(text, font=small_font)

    x = WIDTH - w - 40
    y = 60

    draw.text((x, y), text, fill=(255, 255, 255), font=small_font)


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def create_post(image_url, caption, output_path):
    # Load + format image
    img = load_image(image_url)
    img = resize_image(img)
    img = add_gradient(img)

    draw = ImageDraw.Draw(img)

    # Fonts
    fonts = load_fonts()

    # Caption
    draw_caption(draw, caption, fonts)

    # Branding
    img = add_logo(img)
    add_wordmark(draw, fonts)

    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.convert("RGB").save(output_path, quality=95)

    return output_path


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    create_post(
        "https://images.pexels.com/photos/274506/pexels-photo-274506.jpeg",
        "This win exposes deeper cracks\nIndia still struggles under pressure\nBig teams will punish this weakness",
        "output/test.jpg"
    )
