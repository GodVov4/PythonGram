import cloudinary.uploader
from PIL import Image
from io import BytesIO
import qrcode


class CloudService:
    @staticmethod
    async def upload_picture(user_id, image_file):
        folder_name = f"PythonGram/user_{user_id}/original_images"
        response = cloudinary.uploader.upload(
            image_file,
            folder=folder_name
        )
        return response['url']

    @staticmethod
    async def upload_transformed_picture(user_id, image_url, transformation_params):
        folder_name = f"PythonGram/user_{user_id}/transformed_images"
        response = cloudinary.uploader.upload(
            image_url,
            transformation=transformation_params,
            folder=folder_name
        )
        return response['url']

    @staticmethod
    async def delete_picture(public_id):
        cloudinary.uploader.destroy(public_id)

    @staticmethod
    async def upload_qr_code(user_id, img: Image.Image):
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        folder_name = f"PythonGram/user_{user_id}/qr_codes"
        response = cloudinary.uploader.upload(buffer, folder=folder_name)
        return response['url']

    @staticmethod
    def generate_qr_code(url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img