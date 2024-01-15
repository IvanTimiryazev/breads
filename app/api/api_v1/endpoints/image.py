from typing import Any, Annotated, List
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.crud.crud_comment import comment
from app.schemas import image
from app.schemas.comment import CommentDBOut, CommentCreate, CommentDBCreate
from app.schemas.exceptions import ErrorResponse
from app.schemas.responses import SuccessResponse
from app.models.users import Users
from app.models.image import Image
from app.utils.image_processing import image_processing, image_delete, image_exist_check
from app.core.config import settings


router = APIRouter()


@router.post("/upload", response_model=image.ImageDBOut, status_code=status.HTTP_201_CREATED)
def upload_image(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		file: Annotated[UploadFile, File(...)]
) -> Any:
	name = image_processing(file)
	image_obj = image.ImageDB(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
	db_image = Image(**image_obj.model_dump())
	db.add(db_image)
	db.commit()
	return db_image


@router.post("/uploadfiles", response_model=image.ImagesDBOut, status_code=status.HTTP_201_CREATED)
def upload_images(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		files: Annotated[List[UploadFile], File(...)]
) -> Any:
	for file in files:
		name = image_processing(file)
		image_obj = image.ImageDB(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
		db_image = Image(**image_obj.model_dump())
		db.add(db_image)
		db.commit()
	images_out = [image.ImageDBOut.model_validate(elem) for elem in current_user.images.all()]
	return {"images": images_out}


@router.get("/get-all", response_model=image.ImagesOut, status_code=status.HTTP_200_OK)
def get_images(
		*,
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	_url = Path(f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/static/images")
	images_out = [image.ImageOut(filepath=_url/i.name, name=i.name) for i in current_user.images.all()]
	return {"images": images_out}


@router.delete("/image/{filename}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def delete_image(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		filename: str
) -> Any:
	image_delete(filename)
	db_image = db.execute(select(Image).filter_by(name=filename)).scalar_one_or_none()
	current_user.images.remove(db_image)
	db.commit()
	return {"success": "Image has been deleted."}


@router.get("/download/{filename}", status_code=status.HTTP_200_OK)
def download_image(
		*,
		current_user: Annotated[Users, Depends(get_current_user)],
		filename: str
) -> FileResponse:
	filepath = image_exist_check(filename)
	return FileResponse(filepath)


@router.post("/{filename}/comment", response_model=CommentDBOut, status_code=status.HTTP_201_CREATED)
def create_comment(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		filename: str,
		obj_in: CommentCreate
) -> Any:
	"""Создает комментарий к фото."""
	filepath = image_exist_check(filename)
	db_image = db.execute(select(Image).filter_by(name=filename)).scalar_one_or_none()
	comment_obj = CommentDBCreate(**obj_in.model_dump(), user_id=current_user.id)
	db_comment = comment.create(db, obj_in=comment_obj, obj_to_comment=db_image)
	return db_comment


@router.get("/{filename}", response_model=image.ImageOut, status_code=status.HTTP_200_OK)
def get_image(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		filename: str
) -> Any:
	filepath = image_exist_check(filename)
	db_image = db.execute(select(Image).filter_by(name=filename)).scalar_one_or_none()
	if not db_image:
		error_response = ErrorResponse(
			loc="filename",
			msg="The image with this id does not exists",
			type="value_error"
		)
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=[error_response.model_dump()]
		)
	url = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/static/images/{filename}"
	_image = image.ImageDBOut.model_validate(db_image)
	_image = _image.model_dump()
	_image["filepath"] = url
	return _image

