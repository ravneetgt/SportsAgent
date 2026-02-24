from PIL import Image, ImageDraw, ImageFont


def create_post(image_path, title, caption, output_path):
    print("create_post called")

    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # -----------------------------
    # GRADIENT OVERLAY
    # -----------------------------
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    for y in range(height):
        opacity = int(180 * (y / height))
        overlay_draw.line([(0, y), (width, y)], fill=(0, 0, 0, opacity))

    img = Image.alpha_composite(img.convert('RGBA'), overlay)

    draw = ImageDraw.Draw(img)

    # -----------------------------
    # FONTS
    # -----------------------------
    title_font = ImageFont.truetype("Arial.ttf", 60)
    caption_font = ImageFont.truetype("Arial.ttf", 40)

    # -----------------------------
    # TITLE
    # -----------------------------
    draw.text(
        (50, height - 250),
        title[:80],
        font=title_font,
        fill=(255, 255, 255)
    )

    # -----------------------------
    # CAPTION
    # -----------------------------
    draw.text(
        (50, height - 150),
        caption[:100],
        font=caption_font,
        fill=(200, 200, 200)
    )

    # -----------------------------
    # LOGO (IMPORTANT)
    # -----------------------------
    try:
        logo = Image.open("logo.png").convert("RGBA")

        logo.thumbnail((150, 150))

        img.paste(logo, (50, 50), logo)
    except:
        print("Logo not found")

    # -----------------------------
    # WORDMARK
    # -----------------------------
    draw.text(
        (50, 200),
        "GAMETRAIT",
        font=caption_font,
        fill=(255, 255, 255)
    )

    # -----------------------------
    # SAVE
    # -----------------------------
    img = img.convert("RGB")
    img.save(output_path)

    return output_path