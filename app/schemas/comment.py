from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.users import UserOut


class CommentCreate(BaseModel):
	text: str
	parent_comment_id: int | None = None


class CommentUpdate(BaseModel):
	text: str


class CommentDBCreate(CommentCreate):
	model_config = ConfigDict(from_attributes=True)

	created_at: datetime | None = None
	updated_at: datetime | None = None
	user_id: int


class CommentDBUpdate(CommentUpdate):
	updated_at: datetime


class CommentDBOut(CommentDBCreate):
	id: int
	author: UserOut | None = None
	parent_comment: Optional["CommentDBOut"] = None
	child_comments: Optional[List["CommentDBOut"]] = None
	commentable_type: str
	commentable_id: int


