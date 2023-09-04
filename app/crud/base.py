from typing import Any, Dict, List, Tuple, TypeVar, Generic, Type, Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

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

	def get(self, db: Session, *, id: Any) -> ModelType | None:
		"""Возвращает объект по id"""
		return db.query(self.model).filter_by(id=id).first()

	def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
		"""Возвращает коллекцию объектов. skip - номер записи с которой начать выгрузку. limit - лимит"""
		return db.query(self.model).offset(skip).limit(limit).all()

	def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
		"""Создаем новый объект"""
		obj_data = obj_in.dict()
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
			update_data = obj_in.dict(exclude_unset=True)
		for field in obj_data:
			if field in update_data:
				setattr(db_obj, field, update_data[field])
		db.add(db_obj)
		db.commit()
		db.refresh(db_obj)
		return db_obj

	def remove(self, db: Session, *, id: int) -> ModelType:
		"""Удаление объекта по id в бд"""
		obj = db.query(self.model).get(id)
		db.delete(obj)
		db.commit()
		return obj
