import os
import uuid
import shutil
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.schemas.exceptions import ErrorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def image_exist_check(filename: str) -> Path | None:
	filepath = Path(settings.STATIC_DIR) / "images" / filename
	if not os.path.exists(filepath):
		error_response = ErrorResponse(
			loc="filename",
			msg="Image not found",
			type="TypeError"
		)
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=[error_response.model_dump()])
	return filepath


def image_processing(image: UploadFile) -> str | None:
	filepath = Path(settings.STATIC_DIR)/"images"
	extension = image.filename.split(".")[-1].lower()
	if extension not in ('jpg', 'jpeg', 'png'):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid file type"
		)
	name = uuid.uuid4().hex + "." + extension
	with open(Path(filepath)/name, "wb") as buffer:
		shutil.copyfileobj(image.file, buffer)
	return name


def image_delete(filename: str) -> None:
	filepath = Path(settings.STATIC_DIR) / "images" / filename
	if not os.path.exists(filepath):
		error_response = ErrorResponse(
			loc="filename",
			msg="Image not found",
			type="TypeError"
		)
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=[error_response.model_dump()])
	try:
		os.remove(filepath)
	except Exception as e:
		logger.error("Image could not be deleted")
		error_response = ErrorResponse(
			loc="filename",
			msg="Image could not be deleted",
			type="TypeError"
		)
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=[error_response.model_dump()])

