from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.post import Post
from app.models.users import Users
from app.schemas.post import PostDBCreate, PostUpdate


class CRUDPost(CRUDBase[Post, PostDBCreate, PostUpdate]):
	pass


post = CRUDPost(Post)


