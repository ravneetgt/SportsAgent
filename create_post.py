from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

WIDTH = 1080
HEIGHT = 1350
PADDING = 80


def wrap_text(text, width=20):
    return "\n".join(textwrap.wrap(text, width=width))


def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()


def create_post(title, caption, category, index):
    # background
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 15, 20))
    draw = ImageDraw.Draw(img)

    # fonts
    title_font = load_font("Arial Bold.ttf", 90)
    caption_font = load_font("Arial.ttf", 42)
    small_font = load_font("Arial.ttf", 30)

    # shorten title
    short_title = " ".join(title.split()[:6])
    title_text = wrap_text(short_title.upper(), 12)

    # use first line of caption
    first_line = caption.split("\n")[0]
    caption_text = wrap_text(first_line, 25)

    # category color
    if category == "cricket":
        accent = (80, 180, 120)
    else:
        accent = (120, 140, 255)

    # category label
    draw.text(
        (PADDING, 120),
        category.upper(),
        font=small_font,
        fill=accent
    )

    # title
    draw.text(
        (PADDING, 300),
        title_text,
        font=title_font,
        fill=(255, 255, 255)
    )

    # caption
    draw.text(
        (PADDING, 750),
        caption_text,
        font=caption_font,
        fill=(180, 180, 180)
    )

    # brand
    draw.text(
        (PADDING, HEIGHT - 120),
        "EDGE OF PLAY",
        font=small_font,
        fill=(120, 120, 120)
    )

    # save
    os.makedirs("posts", exist_ok=True)
    path = f"posts/post_{index}.jpg"
    img.save(path, quality=95)

    return path


# test
if __name__ == "__main__":
    p = create_post(
        "India beat Pakistan in thriller",
        "India didn’t dominate this.\nPakistan collapsed under pressure.",
        "cricket",
        1
    )
    print(p)