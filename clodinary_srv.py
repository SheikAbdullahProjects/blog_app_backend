import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_img(file, folder_name="chat_app"):
    try:
        result = cloudinary.uploader.upload(
            file=file,
            folder=folder_name,
            resource_type="auto"
        )
        return result
    except Exception as exp:
        raise Exception(f"Upload failed: {str(exp)}")
    
    
def delete_img(public_key : str):
    try:
        result = cloudinary.uploader.destroy(public_key)
        return result
    except Exception as exp:
        raise Exception(f"Upload failed: {str(exp)}")