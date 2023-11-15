import json
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.users import UserOut
from app.schemas.image import ImageDBOut


class PostCreate(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	content: str | None = None
	original_post_id: int | None = None

	@model_validator(mode='before')
	@classmethod
	def to_py_dict(cls, data: str) -> dict:
		return json.loads(data)

	@model_validator(mode='after')
	def original_post_id_check(self):
		if self.original_post_id == 0:
			self.original_post_id = None
		return self


class PostUpdate(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	content: str | None = None

	@model_validator(mode='before')
	@classmethod
	def to_py_dict(cls, data: str) -> dict:
		return json.loads(data)


class PostDBCreate(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	content: str | None = None
	created_at: datetime | None = None
	updated_at: datetime | None = None
	user_id: int
	original_post_id: int | None = None


class PostDBUpdate(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	content: str | None = None
	updated_at: datetime


class PostDBOut(PostDBCreate):
	id: int
	author: UserOut | None = None
	original_post: Optional["PostDBOut"] = None
	images: List[ImageDBOut] | None = None


class PostsDBOut(BaseModel):
	posts: List[PostDBOut]