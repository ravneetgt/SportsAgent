import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

def _get(name):
    # works both locally and on Streamlit
    return os.getenv(name)

cloudinary.config(
    cloud_name=_get("CLOUDINARY_CLOUD_NAME"),
    api_key=_get("CLOUDINARY_API_KEY"),
    api_secret=_get("CLOUDINARY_API_SECRET"),
)

def upload_image(file_path):
    try:
        if not os.path.exists(file_path):
            print("File not found:", file_path)
            return None

        res = cloudinary.uploader.upload(
            file_path,
            folder="sportsagent",
            resource_type="image"
        )

        url = res.get("secure_url")
        print("UPLOADED:", url)
        return url

    except Exception as e:
        print("Upload error:", e)
        return None


# test
if __name__ == "__main__":
    print(upload_image("output/test.jpg"))
