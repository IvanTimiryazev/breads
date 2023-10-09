from typing import List, Optional
from datetime import datetime

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Image(Base):
	__tablename__ = "image"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(40), unique=True)
	upload_time: Mapped[datetime]
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

	def __repr__(self):
		return f"name: {self.name}, user_id: {self.user_id}, created: {self.upload_time}"

