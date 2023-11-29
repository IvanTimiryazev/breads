from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import Text, DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_relationship

from app.db.base_class import Base
if TYPE_CHECKING:
	from app.models.users import Users


class Comment(Base):
	__tablename__ = "comment"

	id: Mapped[int] = mapped_column(primary_key=True)
	text: Mapped[str] = mapped_column(Text)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime | None]
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
	parent_comment_id: Mapped[int | None] = mapped_column(ForeignKey("comment.id"))
	commentable_type: Mapped[str] = mapped_column(String(50))
	commentable_id: Mapped[int] = mapped_column(Integer)
	author: Mapped["Users"] = relationship(back_populates="comments")
	parent_comment: Mapped["Comment"] = relationship(back_populates="child_comments", remote_side=[id])
	child_comments: Mapped[List["Comment"]] = relationship(back_populates="parent_comment", lazy="selectin")

	# https://sqlalchemy-utils.readthedocs.io/en/latest/generic_relationship.html
	commentable = generic_relationship(commentable_type, commentable_id)

	def __repr__(self) -> str:
		return f"id:{self.id}, type: {self.commentable_type}, commentable_id: {self.commentable_id}"
