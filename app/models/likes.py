from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_relationship

from app.db.base_class import Base


class Likes(Base):
	__tablename__ = "likes"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	entity_type: Mapped[str] = mapped_column(String(50))
	entity_id: Mapped[int] = mapped_column(Integer)
	# https://sqlalchemy-utils.readthedocs.io/en/latest/generic_relationship.html
	entity = generic_relationship(entity_type, entity_id)

	def __repr__(self) -> str:
		return f"id: {self.id} - user: {self.user_id} - type: {self.entity_type}"
