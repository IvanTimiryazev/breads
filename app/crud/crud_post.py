from typing import Any

from sqlalchemy.orm import Session

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


post = CRUDPost(Post)

