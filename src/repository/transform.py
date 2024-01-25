import qrcode

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import TransformedPicture, Picture
from src.services.cloudstore import CloudService


class TransformRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transformed_picture(
            self, user_id: int,
            original_picture_id: int,
            transformation_params: dict,
    ):
        """
        The create_transformed_picture method creates a new transformed picture.

        :param user_id: The ID of the user uploading the image.
        :param original_picture_id: The ID of the original picture.
        :param transformation_params: The transformation parameters to be applied to the image.
        :return: The transformed picture.
        """
        original_picture = await self.get_picture_by_id(original_picture_id)
        if not original_picture:
            return None
        try:
            transformed_url, public_id = await CloudService.upload_transformed_picture(
                user_id, original_picture.url, transformation_params)
            qr_image = qrcode.make(transformed_url)
            qr_url, qr_public_id = await CloudService.upload_qr_code(user_id, qr_image)
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
        except Exception:
            return None

    async def update_transformed_picture(
            self, transformed_picture_id: int,
            transformation_params: dict,
    ):
        """
        The update_transformed_picture method updates an existing transformed picture.

        :param transformed_picture_id: The ID of the transformed picture.
        :param transformation_params: The transformation parameters to be applied to the image.
        :return: The updated transformed picture.
        """
        transformed_picture = await self.get_transformed_picture(transformed_picture_id)
        user_id = transformed_picture.user_id
        if not transformed_picture:
            return None
        try:
            new_transformed_url = await CloudService.update_picture_on_cloudinary(
                public_id=transformed_picture.public_id,
                transformation_params=transformation_params
            )
            if not new_transformed_url:
                return None
            new_qr_image = qrcode.make(new_transformed_url)
            new_qr_url, new_qr_public_id = await CloudService.upload_qr_code(user_id, new_qr_image)
            transformed_picture.url = new_transformed_url
            transformed_picture.qr_url = new_qr_url
            transformed_picture.qr_public_id = new_qr_public_id
            self.session.add(transformed_picture)
            await self.session.commit()
            await self.session.refresh(transformed_picture)
            return transformed_picture
        except Exception:
            return None

    async def get_picture_by_id(self, picture_id: int):
        """
        The get_picture_by_id method retrieves a picture by its ID.

        :param picture_id: The ID of the picture to retrieve.
        :return: The retrieved picture.
        """
        query = select(Picture).where(Picture.id == picture_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_transformed_picture(self, transformed_picture_id: int):
        """
        The get_transformed_picture method retrieves a transformed picture by its ID.

        :param transformed_picture_id: The ID of the transformed picture to retrieve.
        :return: The retrieved transformed picture.
        """
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_transforms(self, user_id: int):
        """
        The get_user_transforms method retrieves all transformed pictures for a given user.

        :param user_id: The ID of the user.
        :return: A list of transformed pictures.
        """
        query = select(TransformedPicture).where(TransformedPicture.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete_transformed_picture(self, transformed_picture_id: int):
        """
        The delete_transformed_picture method deletes a transformed picture by its ID.

        :param transformed_picture_id: The ID of the transformed picture to delete.
        :return: True if the transformed picture was deleted successfully, False otherwise.
        """
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
                raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {e}")
            return True
        return False
