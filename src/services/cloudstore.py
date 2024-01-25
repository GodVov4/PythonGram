import asyncio
from io import BytesIO

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from requests.exceptions import RequestException
from PIL import Image
from fastapi import HTTPException, UploadFile

from src.conf.config import config

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
)


class CloudService:
    @staticmethod
    async def upload_picture(user_id: int, image_file: UploadFile, folder_name: str = None):
        """
        The upload_picture method uploads an image to Cloudinary and returns its URL and public ID.

        :param folder_name:
        :param user_id: The ID of the user uploading the image.
        :param image_file: The image file to be uploaded.
        :return: A dictionary containing the URL and public ID of the uploaded image.
        """
        try:
            if not folder_name:
                folder_name = f"PythonGram/user_{user_id}/original_images"
            response = await asyncio.to_thread(
                cloudinary.uploader.upload,
                image_file.file,
                folder=folder_name,
            )
            return response['url'], response['public_id']
        except CloudinaryError as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження зображення: {e}")

    @staticmethod
    async def upload_transformed_picture(user_id: int, image_url: str, transformation_params: dict):
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
                folder=folder_name,
            )
            return response['url'], response['public_id']
        except CloudinaryError as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження зображення: {e}")

    @staticmethod
    async def delete_picture(public_id: str):
        """
        The delete_picture method deletes an image from Cloudinary.

        :param public_id: The public ID of the image to be deleted.
        """
        try:
            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка видалення зображення: {e}")

    @staticmethod
    async def upload_qr_code(user_id: int, img: Image.Image):
        """
        The upload_qr_code method uploads an image to Cloudinary and returns its URL and public ID.

        :param user_id: The ID of the user uploading the image.
        :param img: The image to be uploaded.
        :return: A dictionary containing the URL and public ID of the uploaded image.
        """
        try:
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            folder_name = f"PythonGram/user_{user_id}/qr_codes"
            response = await asyncio.to_thread(cloudinary.uploader.upload, buffer, folder=folder_name)
            return response['url'], response['public_id']
        except CloudinaryError as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження QR-коду: {e}")

    @staticmethod
    async def update_picture_on_cloudinary(public_id: str, transformation_params: dict):
        """
        The update_picture_on_cloudinary method updates an image on Cloudinary.

        :param public_id: The public ID of the image to be updated.
        :param transformation_params: The transformation parameters to be applied to the image.
        :return: The URL of the updated image.
        """
        # print(f"Updating picture on Cloudinary: {public_id} with transformations {transformation_params}")
        try:
            response = await asyncio.to_thread(
                cloudinary.uploader.explicit,
                public_id,
                type='upload',
                eager=[transformation_params]
            )

            # print(f"Response from Cloudinary: {response}")

            if 'eager' in response and response['eager']:
                eager_transformed_url = response['eager'][0]['url']
            else:
                return None
            return eager_transformed_url
        except CloudinaryError as e:
            raise HTTPException(status_code=500, detail=f"Cloudinary error: {e}")
        except RequestException as e:
            raise HTTPException(status_code=500, detail=f"Network error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка завантаження зображення: {e}")
