import asyncio
from io import BytesIO

import cloudinary
import cloudinary.uploader
from PIL import Image
from fastapi import HTTPException

from src.conf.config import config

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
)


class CloudService:
    @staticmethod
    async def upload_picture(user_id, image_file):
        """
        The upload_picture method uploads an image to Cloudinary and returns its URL and public ID.

        :param user_id: The ID of the user uploading the image.
        :param image_file: The image file to be uploaded.
        :return: A dictionary containing the URL and public ID of the uploaded image.
        """
        try:
            folder_name = f"PythonGram/user_{user_id}/original_images"
            response = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_file,
                folder=folder_name  # TODO: Check it - "Expected type 'dict[str, Any]', got 'str' instead"
            )
            return response['url'], response['public_id']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження зображення: {e}")

    @staticmethod
    async def upload_transformed_picture(user_id, image_url, transformation_params):
        """
        The upload_transformed_picture method uploads an image to Cloudinary and returns its URL and public ID.

        :param user_id: The ID of the user uploading the image.
        :param image_url: The URL of the image to be uploaded.
        :param transformation_params: The transformation parameters to be applied to the image.
        :return: A dictionary containing the URL and public ID of the uploaded image.
        """
        try:
            folder_name = f"PythonGram/user_{user_id}/transformed_images"
            response = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_url,
                transformation=transformation_params,
                folder=folder_name  # TODO: Check it - "Expected type 'dict[str, Any]', got 'str' instead"
            )
            return response['url'], response['public_id']
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження трансформованого зображення: {e}")

    @staticmethod
    async def delete_picture(public_id):
        """
        The delete_picture method deletes an image from Cloudinary.

        :param public_id: The public ID of the image to be deleted.
        :return: None
        """
        try:
            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка видалення зображення: {e}")

    @staticmethod
    async def upload_qr_code(user_id, img: Image.Image):
        """
        The upload_qr_code method uploads an image to Cloudinary and returns its URL and public ID.

        :param user_id: The ID of the user uploading the image.
        :param img: The image to be uploaded.
        :return: A dictionary containing the URL and public ID of the uploaded image.
        """
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        folder_name = f"PythonGram/user_{user_id}/qr_codes"
        response = await asyncio.to_thread(cloudinary.uploader.upload(buffer, folder=folder_name))
        return response['url'], response['public_id']
