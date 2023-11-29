from typing import TypeVar, List

from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.schemas.comment import CommentDBCreate, CommentDBUpdate
from app.schemas.exceptions import ErrorResponse
from app.models.comment import Comment
from app.models.users import Users
from app.models.post import Post
from app.db.base_class import Base

T = TypeVar("T", bound=Base)


class CRUDComment(CRUDBase[Comment, CommentDBCreate, CommentDBUpdate]):
	def get(self, db: Session, *, id_: int) -> Comment | None:
		"""Возвращает комментарий по его ID. После выполняет проверку, существует ли такой комментарий.
		Если db_comment is None, то будет исключение."""
		db_comment = db.get(self.model, id_)
		if not db_comment:
			error_response = ErrorResponse(
				loc="comment_id",
				msg="The comment with this id does not exists",
				type="value_error"
			)
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[error_response.model_dump()]
			)
		return db_comment

	def create(
			self,
			db: Session,
			*,
			obj_in: CommentDBCreate,
			obj_to_comment: T = None
	) -> Comment:
		db_comment = self.model(**obj_in.model_dump())
		db_comment.commentable = obj_to_comment
		db.add(db_comment)
		db.commit()
		return db_comment

	def get_object_comments(
			self,
			db: Session,
			*,
			obj_to_comment: T
	) -> List[Comment] | None:
		stmt = select(self.model).where(
			self.model.commentable == obj_to_comment, self.model.parent_comment_id.is_(None))
		return db.execute(stmt).scalars().all()


comment = CRUDComment(Comment)
