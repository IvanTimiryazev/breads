from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
	from app.models.image import Image
	from app.models.users import Users


class Post(Base):
	__tablename__ = "post"

	id: Mapped[int] = mapped_column(primary_key=True)
	content: Mapped[str | None] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime | None]
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	original_post_id: Mapped[int | None] = mapped_column(ForeignKey("post.id"))
	author: Mapped["Users"] = relationship(back_populates="posts")
	original_post: Mapped["Post"] = relationship(remote_side=[id])
	images: Mapped[List["Image"]] = relationship(back_populates="post", lazy="dynamic", cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"id: {self.id}, created: {self.created_at}, user_id: {self.user_id}"

