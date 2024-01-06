from typing import TypeVar

from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.crud.base import CRUDBase
from app.models.likes import Likes
from app.schemas.like import LikeCreate, LikeUpdate
from app.db.base_class import Base
from app.schemas.exceptions import ErrorResponse

T = TypeVar('T', bound=Base)


class CRUDLikes(CRUDBase[Likes, LikeCreate, LikeUpdate]):
	def get_before_create(self, db: Session, *, obj_to_like: T, user_id: int) -> Likes | None:
		"""Делаем запрос на наличие лайка по сущности и user_id"""
		stmt = select(self.model).where(
			self.model.entity == obj_to_like, self.model.user_id == user_id
		)
		return db.execute(stmt).scalar_one_or_none()

	def create(
			self,
			db: Session,
			*,
			obj_in: LikeCreate,
			obj_to_like: T = None
	) -> Likes | None:
		"""Проверяю нет ли такого лайка, если нет то создаю запись"""
		if self.get_before_create(db, obj_to_like=obj_to_like, user_id=obj_in.user_id):
			error_response = ErrorResponse(
				loc="obj_to_like",
				msg="You are already liked this entity",
				type="value_error"
			)
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=[error_response.model_dump()]
			)
		db_like = self.model(**obj_in.model_dump())
		db_like.entity = obj_to_like
		db.add(db_like)
		db.commit()
		return db_like

	def remove_like(
			self,
			db: Session,
			*,
			obj_to_like: T,
			user_id: int
	) -> dict | None:
		"""проверяю есть ли такой лайк, если есть то удаляю"""
		db_like = self.get_before_create(db, obj_to_like=obj_to_like, user_id=user_id)
		if not db_like:
			error_response = ErrorResponse(
				loc="obj_to_like",
				msg="The like with this id does not exists",
				type="value_error"
			)
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=[error_response.model_dump()]
			)
		db.delete(db_like)
		db.commit()
		return {"status": "Deleted"}

	def count_likes(
			self,
			db: Session,
			*,
			obj_to_like: T
	) -> int:
		"""Делаем подсчет лайков у сущности"""
		stmt = select(func.count("*")).select_from(self.model).where(self.model.entity == obj_to_like)
		return db.execute(stmt).scalar_one()


likes = CRUDLikes(Likes)






