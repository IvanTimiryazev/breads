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
	commentable_type: str
	commentable_id: int
	parent_comment: Optional["CommentDBOut"] = None


# чтобы избежать бесконечной рекурсии, вынес child_comments в отдельный подкласс
# так как parent_comment и child_comments ссылались бы на себя
class CommentDBOutWithComments(CommentDBOut):
	child_comments: None | List["CommentDBOutWithComments"] = []


CommentDBOutWithComments.model_rebuild()


class CommentsDBOut(BaseModel):
	comments: List[CommentDBOutWithComments] | None = []

