from datetime import date
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import DeclarativeBase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, generics


class Base(DeclarativeBase):
    pass


class Picture(Base):
    __tablename__ = 'pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    # tags = Mapped[List] = mapped_column


    # user_id: Mapped[generics.GUID] = mapped_column(generics.GUID(), ForeignKey('user.id'), nullable=True)
    # user: Mapped["User"] = relationship("User", backref="pictures", lazy="joined")

# class Tag(Base):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(50), nullable=False)


