from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap
import os


WIDTH = 1080
HEIGHT = 1350

PADDING = 80
TEXT_WIDTH = WIDTH - (PADDING * 2)


def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("Helvetica-Bold.ttf", size)
        return ImageFont.truetype("Helvetica.ttf", size)
    except:
        return ImageFont.load_default()


def download_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        return img
    except:
        return None


def resize_crop(img):
    img_ratio = img.width / img.height
    target_ratio = WIDTH / HEIGHT

    if img_ratio > target_ratio:
        new_height = HEIGHT
        new_width = int(img_ratio * new_height)
    else:
        new_width = WIDTH
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height))

    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2

    return img.crop((left, top, left + WIDTH, top + HEIGHT))


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        w, h = draw.textbbox((0, 0), test_line, font=font)[2:]
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_multiline_centered(draw, lines, font, y_start):
    y = y_start

    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:]
        x = (WIDTH - w) / 2

        draw.text((x, y), line, fill="white", font=font)
        y += h + 10

    return y


def create_post(image_url, title, caption, output_path="output/post.jpg"):
    base = download_image(image_url)

    if base is None:
        print("Image failed")
        return None

    base = resize_crop(base)

    # overlay gradient
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 120))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(base)

    # -----------------------
    # FONTS
    # -----------------------
    title_font = load_font(60, bold=True)
    caption_font = load_font(38)
    brand_font = load_font(32)

    # -----------------------
    # TITLE WRAP
    # -----------------------
    title = title.split("-")[0].strip()  # clean source names
    title_lines = wrap_text(title, title_font, TEXT_WIDTH, draw)

    # limit lines
    title_lines = title_lines[:3]

    # -----------------------
    # CAPTION WRAP
    # -----------------------
    caption_lines = wrap_text(caption, caption_font, TEXT_WIDTH, draw)
    caption_lines = caption_lines[:4]

    # -----------------------
    # POSITIONING
    # -----------------------
    total_height = 0

    for line in title_lines:
        _, h = draw.textbbox((0, 0), line, font=title_font)[2:]
        total_height += h + 10

    total_height += 20

    for line in caption_lines:
        _, h = draw.textbbox((0, 0), line, font=caption_font)[2:]
        total_height += h + 8

    y_start = HEIGHT - total_height - 150

    # -----------------------
    # DRAW TITLE
    # -----------------------
    y = draw_multiline_centered(draw, title_lines, title_font, y_start)

    y += 20

    # -----------------------
    # DRAW CAPTION
    # -----------------------
    y = draw_multiline_centered(draw, caption_lines, caption_font, y)

    # -----------------------
    # BRAND TEXT (bottom right)
    # -----------------------
    brand_text = "GAMETRAIT"
    w, h = draw.textbbox((0, 0), brand_text, font=brand_font)[2:]

    draw.text(
        (WIDTH - w - 40, HEIGHT - h - 40),
        brand_text,
        fill=(255, 255, 255, 200),
        font=brand_font
    )

    # -----------------------
    # WATERMARK (top left)
    # -----------------------
    logo_path = "logo.png"

    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((120, 120))

        logo.putalpha(80)

        base.paste(logo, (40, 40), logo)

    # -----------------------
    # SAVE
    # -----------------------
    os.makedirs("output", exist_ok=True)
    base = base.convert("RGB")
    base.save(output_path, quality=95)

    return output_path
