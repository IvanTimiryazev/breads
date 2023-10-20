from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
	from app.models.post import Post


class Image(Base):
	__tablename__ = "image"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(40), unique=True)
	upload_time: Mapped[datetime]
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	post_id: Mapped[int | None] = mapped_column(ForeignKey("post.id"), index=True)
	post: Mapped["Post"] = relationship(back_populates="images")

	def __repr__(self):
		return f"name: {self.name}, user_id: {self.user_id}, created: {self.upload_time}"

