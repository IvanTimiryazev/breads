from datetime import date
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Table, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped

from app.db.base_class import Base
from app.models.post import Post
from app.models.image import Image
from app.models.comment import Comment
from app.models.likes import Likes


# follower_id - следящий, followed_id - следуемый
following = Table(
	'following', Base.metadata,
	Column('follower_id', Integer, ForeignKey('users.id')),
	Column('followed_id', Integer, ForeignKey('users.id'))
)


class Users(Base):
	__tablename__ = 'users'

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
	name: Mapped[str | None] = mapped_column(String(50))
	surname: Mapped[str | None] = mapped_column(String(80))
	birth_date: Mapped[date | None]
	about_me: Mapped[str | None] = mapped_column(Text)
	hashed_password: Mapped[str | None] = mapped_column(String(200))

	# В документации sqlalchemy увидел что предпочтительнее использовать back_populates
	# Надо подумать, возможно редактировать определение связи
	# https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#self-referential-many-to-many
	followers = relationship(
		'Users', secondary=following,
		primaryjoin=id == following.c.follower_id,
		secondaryjoin=id == following.c.followed_id,
		backref=backref('followed', lazy='dynamic'),
		lazy='dynamic'
	)
	images: Mapped[List["Image"]] = relationship(lazy="dynamic", cascade="all, delete-orphan")
	posts: Mapped[List["Post"]] = relationship(back_populates="author", lazy="dynamic", cascade="all, delete-orphan")
	comments: Mapped[List["Comment"]] = relationship(
		back_populates="author", lazy="dynamic", cascade="all, delete-orphan"
	)
	likes: Mapped[List["Likes"]] = relationship(lazy="dynamic", cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"User_id={self.id} - {self.email}"

	# при обращении к атрибуту followers (кто подписан) используется такой запрос
	# select * from users inner join following on users.id = following.followed_id where following.follower_id = 2
	# при обращении к атрибуту followed (на кого подписан) используется такой запрос
	# select * from users inner join following on users.id = following.follower_id where following.followed_id = 3;
