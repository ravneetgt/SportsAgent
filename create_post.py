from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os


# -----------------------------
# CONFIG
# -----------------------------
OUTPUT_FOLDER = "output"
LOGO_PATH = "assets/logo.png"


# -----------------------------
# CREATE POST IMAGE
# -----------------------------
def create_post(image_url, title, caption):
    try:
        if not image_url:
            print("No image URL")
            return None

        # -----------------------------
        # LOAD IMAGE
        # -----------------------------
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        img = img.resize((1080, 1350))

        # -----------------------------
        # DARK OVERLAY (premium look)
        # -----------------------------
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for y in range(img.height):
            opacity = int(180 * (y / img.height))
            draw.line((0, y, img.width, y), fill=(0, 0, 0, opacity))

        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)

        # -----------------------------
        # FONTS
        # -----------------------------
        try:
            font_title = ImageFont.truetype("Helvetica.ttc", 60)
            font_caption = ImageFont.truetype("Helvetica.ttc", 38)
            font_brand = ImageFont.truetype("Helvetica.ttc", 42)
        except:
            font_title = ImageFont.load_default()
            font_caption = ImageFont.load_default()
            font_brand = ImageFont.load_default()

        # -----------------------------
        # TITLE TEXT
        # -----------------------------
        short_title = title[:70] + "..."
        draw.text((40, 900), short_title, fill="white", font=font_title)

        # -----------------------------
        # CAPTION TEXT
        # -----------------------------
        draw.text((40, 1020), caption[:200], fill="white", font=font_caption)

        # -----------------------------
        # LOGO WATERMARK (TOP LEFT)
        # -----------------------------
        if os.path.exists(LOGO_PATH):
            logo = Image.open(LOGO_PATH).convert("RGBA")

            # resize
            logo_width = 160
            ratio = logo_width / logo.width
            logo = logo.resize((logo_width, int(logo.height * ratio)))

            # make it subtle
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.25))
            logo.putalpha(alpha)

            # position top-left
            img.paste(logo, (40, 40), logo)

        else:
            print("Logo not found:", LOGO_PATH)

        # -----------------------------
        # WORDMARK (BOTTOM RIGHT)
        # -----------------------------
        wordmark = "gametrait"

        # measure text
        bbox = draw.textbbox((0, 0), wordmark, font=font_brand)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = img.width - text_width - 40
        y = img.height - text_height - 40

        # subtle opacity
        draw.text(
            (x, y),
            wordmark,
            fill=(255, 255, 255, 180),
            font=font_brand
        )

        # -----------------------------
        # SAVE
        # -----------------------------
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        filename = f"{abs(hash(title))}.jpg"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        img.convert("RGB").save(output_path, quality=95)

        return output_path

    except Exception as e:
        print("Post generation error:", e)
        return None


# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":
    test_image = "https://images.pexels.com/photos/3621104/pexels-photo-3621104.jpeg"

    path = create_post(
        test_image,
        "India vs Australia thriller",
        "India chase down 280 under pressure"
    )

    print(path)
