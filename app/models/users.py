from sqlalchemy import Column, Table, Integer, String, ForeignKey, Date, Text
from sqlalchemy.orm import relationship, backref

from app.db.base_class import Base


following = Table(
	'following', Base.metadata,
	Column('follower_id', Integer, ForeignKey('users.id')),
	Column('followed_id', Integer, ForeignKey('users.id'))
)


class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	email = Column(String(100), unique=True, nullable=False, index=True)
	name = Column(String(50), nullable=True)
	surname = Column(String(80), nullable=True)
	birth_date = Column(Date)
	about_me = Column(Text)
	hashed_password = Column(String(200))
	followers = relationship(
		'Users', secondary=following,
		primaryjoin=id == following.c.follower_id,
		secondaryjoin=id == following.c.followed_id,
		backref=backref('followed', lazy='dynamic'),
		lazy='dynamic'
	)

	def __repr__(self):
		return f"User_id={self.id} - {self.email}"


