import qrcode

from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import TransformedPicture, Picture
from src.schemas.transform import TransformResponse
from src.services.cloudstore import CloudService


class TransformRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transformed_picture(
            self, user_id: int,
            original_picture_id: int,
            transformation_params: dict,
    ):
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

    async def update_transformed_picture(
            self, transformed_picture_id: int,
            transformation_params: dict,
    ):
        # Отримання екземпляра TransformedPicture за transformed_picture_id
        transformed_picture = await self.get_transformed_picture_by_id(transformed_picture_id)
        user_id = transformed_picture.user_id
        if not transformed_picture:
            raise HTTPException(status_code=404, detail="Трансформоване зображення не знайдено")

        try:
            # Повторна трансформація зображення і завантаження на Cloudinary
            new_transformed_url = await CloudService.update_picture_on_cloudinary(
                public_id=transformed_picture.public_id,
                transformation_params=transformation_params
            )

            # Генерація нового QR-коду для трансформованого зображення
            new_qr_image = qrcode.make(new_transformed_url)
            # Оновлення QR коду
            new_qr_url, new_qr_public_id = await CloudService.upload_qr_code(user_id, new_qr_image)

            # Оновлення запису трансформованого зображення у базі даних
            transformed_picture.url = new_transformed_url
            transformed_picture.qr_url = new_qr_url
            transformed_picture.qr_public_id = new_qr_public_id
            self.session.add(transformed_picture)
            await self.session.commit()
            await self.session.refresh(transformed_picture)
            return transformed_picture

        except HTTPException as http_exc:
            # Передача HTTP помилки далі
            raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)

    async def get_picture_by_id(self, picture_id: int):
        # Метод для отримання оригінального зображення за ID
        query = select(Picture).where(Picture.id == picture_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_transformed_picture_by_id(self, transformed_picture_id: int):
        # Метод для отримання трансформованого зображення за ID
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_user_id_by_picture_id(self, picture_id: int):
        picture = await self.get_picture_by_id(picture_id)
        return picture.user_id if picture else None

    async def get_transformed_picture(self, transformed_picture_id: int):
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_transforms(self, user_id: int):
        query = select(TransformedPicture).where(TransformedPicture.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete_transformed_picture(self, transformed_picture_id: int):
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
