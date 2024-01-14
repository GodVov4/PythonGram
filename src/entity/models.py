import enum
from datetime import date

from sqlalchemy import String, ForeignKey, DateTime, func, Enum, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


picture_tag_association = Table(
    'picture_tag_association',
    Base.metadata,
    Column('picture_id', Integer, ForeignKey('pictures.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Picture(Base):
    __tablename__ = 'pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    
    transformed_picture: Mapped["TransformedPicture"] = relationship("TransformedPicture", back_populates="pictures")
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user: Mapped["User"] = relationship("User", back_populates="pictures")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="pictures")
    tags = relationship("Tag", secondary=picture_tag_association, back_populates="pictures")


class Tag(Base):
    __tablename__ = 'tags'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

class TransformedPicture(Base):
    __tablename__ = 'transformed_pictures'
    id: Mapped[int] = mapped_column(primary_key=True)
    original_picture_id: Mapped[int] = mapped_column(ForeignKey('pictures.id'), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    qr_url: Mapped[str] = mapped_column(String(255), nullable=True)
    transformation_params: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now(), nullable=False)
    
    user: Mapped["User"] = relationship("User", back_populates="transformed_pictures")
    original_picture = relationship("Picture", back_populates="transformed_pictures")


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(
        "created_at", DateTime, default=func.now())
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=True)
    ban: Mapped[bool] = mapped_column(default=False, nullable=True)
    
    picture: Mapped["Picture"] = relationship("Picture", back_populates="users", lazy='joined')
    blacklisted_tokens: Mapped["Blacklisted"] = relationship("Blacklisted", backref="users", lazy="joined")
    comment: Mapped["Comment"] = relationship("Comment", back_populates="users", lazy="joined")


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
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    picture_id: Mapped[int] = mapped_column(Integer, ForeignKey("pictures.id"), nullable=True)
    text: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="comments")
    picture = relationship("Picture", back_populates="comments")
