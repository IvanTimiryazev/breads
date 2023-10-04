from typing import Optional
from datetime import date

from sqlalchemy import Column, Table, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref, mapped_column, Mapped

from app.db.base_class import Base


following = Table(
	'following', Base.metadata,
	Column('follower_id', Integer, ForeignKey('users.id')),
	Column('followed_id', Integer, ForeignKey('users.id'))
)


class Users(Base):
	__tablename__ = 'users'

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
	name: Mapped[Optional[str]] = mapped_column(String(50))
	surname: Mapped[Optional[str]] = mapped_column(String(80))
	birth_date: Mapped[Optional[date]]
	about_me: Mapped[Optional[str]] = mapped_column(Text)
	hashed_password: Mapped[Optional[str]] = mapped_column(String(200))

	followers = relationship(
		'Users', secondary=following,
		primaryjoin=id == following.c.follower_id,
		secondaryjoin=id == following.c.followed_id,
		backref=backref('followed', lazy='dynamic'),
		lazy='dynamic'
	)

	def __repr__(self):
		return f"User_id={self.id} - {self.email}"
