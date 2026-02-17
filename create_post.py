from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os


def create_post(image_url, title, caption):
    try:
        if not image_url:
            print("No image URL")
            return None

        # 1. Load image
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")

        # Resize to Instagram
        img = img.resize((1080, 1350))

        # 2. Add gradient overlay (premium look)
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for y in range(img.height):
            opacity = int(200 * (y / img.height))
            draw.line((0, y, img.width, y), fill=(0, 0, 0, opacity))

        img = Image.alpha_composite(img, overlay)

        # 3. Load logo
        logo_path = "assets/logo.png"

        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")

            # Resize logo
            logo_width = 180
            ratio = logo_width / logo.width
            logo = logo.resize((logo_width, int(logo.height * ratio)))

            # Fade logo
            alpha = logo.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.5))
            logo.putalpha(alpha)

            # Position center-bottom
            x = (img.width - logo.width) // 2
            y = img.height - logo.height - 40

            img.paste(logo, (x, y), logo)

        else:
            print("Logo not found at assets/logo.png")

        # 4. Add text
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("Helvetica.ttc", 60)
            font_caption = ImageFont.truetype("Helvetica.ttc", 38)
        except:
            font_title = ImageFont.load_default()
            font_caption = ImageFont.load_default()

        # Shorten title
        short_title = title[:70] + "..."

        draw.text((40, 900), short_title, fill="white", font=font_title)
        draw.text((40, 1020), caption[:220], fill="white", font=font_caption)

        # 5. Save
        os.makedirs("output", exist_ok=True)
        output_path = f"output/post_{abs(hash(title))}.jpg"

        img.convert("RGB").save(output_path, quality=95)

        return output_path

    except Exception as e:
        print("Post generation error:", e)
        return None
