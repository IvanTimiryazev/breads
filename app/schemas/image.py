from typing import List
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, ConfigDict


class ImageDB(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	name: str
	upload_time: datetime
	user_id: int
	post_id: int | None = None


class ImageDBOut(ImageDB):
	id: int


class ImagesDBOut(BaseModel):
	images: List[ImageDBOut]


class ImageOut(ImageDBOut):
	filepath: Path


class ImagesOut(BaseModel):
	images: List[ImageOut]
