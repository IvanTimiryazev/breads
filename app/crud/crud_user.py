from typing import Any, Dict

from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import HTTPException, status

from app.crud.base import CRUDBase
from app.models.users import Users
from app.models.users import following
from app.schemas.users import UserCreate, UserUpdate
from app.schemas.exceptions import ErrorResponse
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[Users, UserCreate, UserUpdate]):
	def get(self, db: Session, *, id_: Any) -> Users | None:
		"""Возвращает юзера по его ID. После выполняет проверку, существует ли такой юзер.
		Если db_user is None, то будет исключение."""
		db_user = db.get(self.model, id_)
		if not db_user:
			error_response = ErrorResponse(
				loc="user_id",
				msg="The user with this id does not exists",
				type="value_error"
			)
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail=[error_response.model_dump()]
			)
		return db_user

	def get_by_email(self, db: Session, *, email: str) -> Users:
		"""Возвращаем объекта класса Users из бд по имэйлу"""
		stmt = select(self.model).filter_by(email=email)
		return db.execute(stmt).scalar_one_or_none()

	def create(self, db: Session, *, obj_in: UserCreate) -> Users:
		"""Создание нового пользователя в бд"""
		obj_in_data = obj_in.model_dump()
		obj_in_data.pop('password')
		db_obj = self.model(**obj_in_data)
		setattr(db_obj, 'hashed_password', get_password_hash(obj_in.password))
		db.add(db_obj)
		db.commit()
		return db_obj

	def update(
			self,
			db: Session,
			*,
			db_obj: Users,
			obj_in: UserUpdate | Dict[str, Any]
	) -> Users:
		"""Изменения данных пользователя в бд"""
		if isinstance(obj_in, dict):
			update_data = obj_in
		else:
			update_data = obj_in.model_dump(exclude_unset=True)
		if 'password' in update_data:
			hashed_password = get_password_hash(update_data['password'])
			del update_data['password']
			update_data['hashed_password'] = hashed_password
		return super().update(db, db_obj=db_obj, obj_in=update_data)

	def authenticate(self, db: Session, *, email: str, password: str) -> Users | None:
		"""Проверяем существует ли юзер и сравниваем предоставленный им пароль с хэшем в бд"""
		auth_user = self.get_by_email(db, email=email)
		if not auth_user:
			return None
		if not verify_password(password=password, hashed_password=auth_user.hashed_password):
			return None
		return auth_user

	@staticmethod
	def is_following(*, user_db: Users, user_to_follow: Users) -> bool:
		"""Здесь получаем список подписок user_db - (select * from following where followed_id = user_db)
		вернет все значения из follower_id которые подходят по условию. Далее проверяю если в колонке
		follower_id есть значение которое равно user_to_follow.id, то счетчик count будет больше 0 и вернет True"""
		return user_db.followed.filter(following.c.follower_id == user_to_follow.id).count() > 0

	@classmethod
	def follow(cls, db: Session, *, user_db: Users, user_to_follow: Users) -> Users | None:
		"""user_db подписывается на user_to_follow. Точнее user_db.followed вернет список из пользователей,
		на которых подписан user_db (select * from following where followed_id = user_db) вернет все значения
		из follower_id которые подходят по условию. Команда user_db.followed.append(user_to_follow) добавит
		пользователя follower в этот список"""
		if not cls.is_following(user_db=user_db, user_to_follow=user_to_follow):
			user_db.followed.append(user_to_follow)
			db.commit()
			return user_db
		else:
			return user_db

	@classmethod
	def unfollow(cls, db: Session, *, user_db: Users, user_to_follow: Users) -> Users | None:
		"""user_db отписывается от user_to_follow. user_db.followed вернет список из пользователей,
		на которых подписан user_db (select * from following where followed_id = user_db) вернет все значения
		из follower_id которые подходят по условию. Команда user_db.followed.remove(user_to_follow) удалит
		follower из этого списка."""
		if cls.is_following(user_db=user_db, user_to_follow=user_to_follow):
			user_db.followed.remove(user_to_follow)
			db.commit()
			return user_db
		else:
			return user_db


user = CRUDUser(Users)
