import unittest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.images import PictureResponseSchema, PictureSchema
from src.entity.models import Picture, User
from src.repository.images import (
    upload_picture,
    delete_picture,
    update_picture_description,
    get_picture,
)


class TestImages(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.image = Picture(id=1, url='test', description='testDEADPOOL',
                            created_at=datetime(2000, 3, 12), updated_at=datetime(2000, 3, 13))
        self.images = [
            self.image,
            Picture(
                id=2,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            ),
            Picture(
                id=3,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            )
        ]

    async def test_get_image(self):
        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image
        result = await get_picture(1, self.session, User())

        # Перевіряємо, чи існує об'єкт Picture і чи не є він None
        self.assertIsNotNone(result, 'Picture object is None')

    async def test_create_image(self):
        body = PictureResponseSchema(
            id=1,
            user_id=1,
            url='test',
            description= None,
            tags=['testDEADPOOL', 'Test S'],
            created_at=datetime(2001, 5, 12),
        )
        result = await upload_picture(body, self.session, User())
        self.assertEqual(result.url, self.image.url)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.tags, body.tags)
        self.assertEqual(result.created_at, body.created_at)
        self.assertTrue(hasattr(result, "id"))

    async def test_delete_image(self):
        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image
        result = await delete_picture(picture_id=1, db=self.session, user=User())
        self.assertEqual(result, self.image)

    async def test_delete_image_not_found(self):
        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_image
        result = await delete_picture(picture_id=1, db=self.session, user=User())
        self.assertIsNone(result, 'db returned object')

    
if __name__ == "__main__":
    unittest.main()

