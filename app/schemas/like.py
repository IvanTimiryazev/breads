from pydantic import BaseModel


class LikeCreate(BaseModel):
	user_id: int


class LikeUpdate(LikeCreate):
	pass


class LikesCount(BaseModel):
	count: int


class LikeDBOut(BaseModel):
	id: int
	user_id: int
	entity_type: str
	entity_id: int
