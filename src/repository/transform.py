import qrcode
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import TransformedPicture, Picture
from src.services.cloudstore import CloudService


class TransformRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transformed_picture(self, user_id, original_picture_id, transformation_params):
        # Отримання екземпляра Picture за original_picture_id
        original_picture = await self.get_picture_by_id(original_picture_id)
        if not original_picture:
            raise HTTPException(status_code=404, detail="Зображення не знайдено")

        try:
            # Трансформація зображення і завантаження на Cloudinary
            transformed_url, public_id = await CloudService.upload_transformed_picture(
                user_id, original_picture.url, transformation_params)
            # Генерація QR-коду для трансформованого зображення
            qr_image = qrcode.make(transformed_url)
            # Завантаження QR-коду на Cloudinary
            qr_url, qr_public_id = await CloudService.upload_qr_code(user_id, qr_image)
            # Створення запису трансформованого зображення у базі даних
            transformed_picture = TransformedPicture(
                original_picture_id=original_picture_id,
                url=transformed_url,
                public_id=public_id,
                qr_url=qr_url,
                qr_public_id=qr_public_id,
                user_id=user_id,
            )
            self.session.add(transformed_picture)
            await self.session.commit()
            await self.session.refresh(transformed_picture)
            return transformed_picture

        except HTTPException as http_exc:
            # Передача HTTP помилки далі
            raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
        except Exception as e:
            # Обробка інших помилок
            raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {e}")

    async def get_picture_by_id(self, picture_id):
        # Метод для отримання оригінального зображення за ID
        query = select(Picture).where(Picture.id == picture_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_id_by_picture_id(self, picture_id: int):
        picture = await self.get_picture_by_id(picture_id)
        return picture.user_id if picture else None

    async def get_transformed_picture(self, transformed_picture_id):
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def delete_transformed_picture(self, transformed_picture_id):
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        transformed_picture = result.scalars().first()
        if transformed_picture:
            try:
                await CloudService.delete_picture(transformed_picture.public_id)
                await CloudService.delete_picture(transformed_picture.qr_public_id)
                await self.session.delete(transformed_picture)
                await self.session.commit()
            except HTTPException as http_exc:
                # Передача помилки до Swagger UI
                raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
            except Exception as e:
                # Обробка інших неочікуваних помилок
                raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {e}")
            return True
        return False

    # def generate_qr_code(self, url):
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(url)
    #     qr.make(fit=True)
    #     img = qr.make_image(fill_color="black", back_color="white")
    #     return img
