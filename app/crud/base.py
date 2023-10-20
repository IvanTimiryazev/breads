from typing import Any, Dict, List, TypeVar, Generic, Type, Sequence

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, Row, RowMapping

from app.db.base_class import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
	def __init__(self, model: Type[ModelType]) -> None:
		"""
		CRUD класс со стандартными методами Create, Read, Update, Delete (CRUD).
		**Parameters**
		* `model`: Модель SQLAlchemy
		"""
		self.model = model

	def get(self, db: Session, *, id_: Any) -> ModelType | None:
		"""Возвращает объект по id"""
		return db.get(self.model, id_)

	def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[Row | RowMapping | Any]:
		"""Возвращает коллекцию объектов. skip - номер записи с которой начать выгрузку. limit - лимит"""
		stmt = select(self.model).offset(skip).limit(limit)
		return db.execute(stmt).scalars().all()

	def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
		"""Создаем новый объект"""
		obj_data = obj_in.model_dump()
		db_obj = self.model(**obj_data)
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj

	def update(
			self,
			db: Session,
			*,
			db_obj: ModelType,
			obj_in: UpdateSchemaType | Dict[str, Any]
	) -> ModelType:
		"""Обновляем объект в бд. Точнее перезаписываем атрибуты в объекте класса ModelTYpe и сохраняем."""
		obj_data = jsonable_encoder(db_obj)
		if isinstance(obj_in, dict):
			update_data = obj_in
		else:
			update_data = obj_in.model_dump(exclude_unset=True)
		for field in obj_data:
			if field in update_data:
				setattr(db_obj, field, update_data[field])
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj

	def remove(self, db: Session, *, id_: int) -> ModelType:
		"""Удаление объекта по id в бд"""
		obj = self.get(db, id_=id_)
		db.delete(obj)
		db.commit()
		return obj
