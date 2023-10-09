from typing import Sequence
from pydantic import BaseModel
from datetime import datetime


class Image(BaseModel):
	name: str
	upload_time: datetime
	user_id: int

	class Config:
		orm_mode = True


class ImageOut(Image):
	id: int


class Images(BaseModel):
	images: Sequence[ImageOut] | None
