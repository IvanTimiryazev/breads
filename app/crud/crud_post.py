from typing import Any, List

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.models.post import Post
from app.models.users import Users
from app.schemas.post import PostDBCreate, PostUpdate
from app.schemas.exceptions import ErrorResponse


class CRUDPost(CRUDBase[Post, PostDBCreate, PostUpdate]):
	def get(self, db: Session, *, id_: Any) -> Post | None:
		db_post = db.get(self.model, id_)
		if not db_post:
			error_response = ErrorResponse(
				loc="post_id",
				msg="The post with this id does not exists",
				type="value_error"
			)
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=[error_response.model_dump()]
			)
		return db_post

	def get_page(self, db: Session, *, page: int, limit: int, id_: int) -> List[Post]:
		"""Функция возвращает посты пользователя, разбитые на страницы"""
		stmt = select(self.model).where(self.model.user_id == id_).offset((page - 1) * limit).limit(limit)
		return db.execute(stmt).scalars().all()

	def count_posts(self, db: Session, id_: int) -> int:
		"""Функция считает общее количество постов пользователя"""
		stmt = select(func.count("*")).select_from(self.model).where(self.model.user_id == id_)
		return db.execute(stmt).scalar_one()


post = CRUDPost(Post)

