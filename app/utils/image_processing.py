import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.core.config import settings


def image_processing(image: UploadFile) -> str:
	filepath = Path(settings.STATIC_DIR)/"images"
	extension = image.filename.split(".")[-1].lower()
	if extension not in ('jpg', 'jpeg', 'png'):
		raise HTTPException(
			status_code=400,
			detail="Invalid file type"
		)
	name = uuid.uuid4().hex + "." + extension
	with open(Path(filepath)/name, "wb") as buffer:
		shutil.copyfileobj(image.file, buffer)
	return name


