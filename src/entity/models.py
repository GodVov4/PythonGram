import enum
from datetime import date
from typing import List
from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


picture_tag_association = Table(
    'picture_tag_association',
    Base.metadata,
    Column('picture_id', Integer, ForeignKey('pictures.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Picture(Base):
    __tablename__ = 'pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    cloudinary_public_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[date] = mapped_column(
        'created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column(
        'updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)

    transformed_pictures: Mapped["TransformedPicture"] = relationship(
        "TransformedPicture", back_populates="original_picture")
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="picture", lazy='joined')
    comment: Mapped[List["Comment"]] = relationship(back_populates="picture", cascade='all, delete', lazy='joined')
    tags: Mapped[List["Tag"]] = relationship(secondary=picture_tag_association, back_populates='pictures', lazy='joined')


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    pictures: Mapped[List["Picture"]] = relationship(secondary=picture_tag_association, back_populates='tags')


class TransformedPicture(Base):
    __tablename__ = 'transformed_pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    original_picture_id: Mapped[int] = mapped_column(ForeignKey('pictures.id'), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    public_id: Mapped[str] = mapped_column(String, nullable=False)  # cloudinary public id
    qr_url: Mapped[str] = mapped_column(String(255), nullable=True)
    qr_public_id: Mapped[str] = mapped_column(String, nullable=True)  # cloudinary public id
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)

    original_picture = relationship("Picture", back_populates="transformed_pictures", lazy='joined')


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    picture_count: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True)

    picture: Mapped["Picture"] = relationship("Picture", back_populates="user", uselist=True, lazy='joined', cascade='all, delete')
    blacklisted_tokens: Mapped["Blacklisted"] = relationship("Blacklisted", back_populates="user", lazy='joined')
    comment: Mapped["Comment"] = relationship("Comment", back_populates="user", lazy='joined', cascade='all, delete')


class Blacklisted(Base):
    __tablename__ = "blacklisted"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    user = relationship("User", back_populates="blacklisted_tokens")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    # onupdate=CASCADE???
    picture_id: Mapped[int] = mapped_column(Integer, ForeignKey(Picture.id), nullable=False)
    picture: Mapped[List["Picture"]] = relationship(back_populates='comment')

    # onupdate=CASCADE???
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="comment")

    # TODO: Help with onupdate, ondelete
