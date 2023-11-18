from typing import Any, Annotated, List
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.schemas.users import UserCreate, UserUpdate, UserOut, UserOutWithFollowers, UserOutWithFollowed
from app.schemas import image
from app.schemas.exceptions import ErrorResponse
from app.schemas.responses import SuccessResponse
from app.models.users import Users
from app.models.image import Image
from app.crud.crud_user import user
from app.elastic.elastic_service import get_es, ElasticSearchService
from app.elastic.documents import UserDoc
from app.utils.image_processing import image_processing, image_delete, image_exist_check
from app.core.config import settings


router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
		*,
		db: Annotated[Session, Depends(get_db)],
		obj_in: UserCreate,
		es: Annotated[ElasticSearchService, Depends(get_es(UserDoc))]
) -> Any:
	user_db = user.get_by_email(db, email=obj_in.email)
	if user_db:
		error_response = ErrorResponse(
			loc="email",
			msg="The user with this email already exists in the system",
			type="value_error"
		)
		raise HTTPException(
			status_code=400,
			detail=[error_response.model_dump()]
		)
	user_db = user.create(db, obj_in=obj_in)
	es.add_to_index(UserOut.model_validate(user_db))
	return user_db


@router.put("/update", response_model=UserOut, status_code=status.HTTP_200_OK)
def update_user(
		*,
		db: Annotated[Session, Depends(get_db)],
		user_in: UserUpdate,
		current_user: Annotated[Users, Depends(get_current_user)],
		es: Annotated[ElasticSearchService, Depends(get_es(UserDoc))]
) -> Any:
	updated_user = user.update(db, db_obj=current_user, obj_in=user_in)
	es.add_to_index(UserOut.model_validate(updated_user))
	return updated_user


@router.post("/follow/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def follow(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_to_follow = user.get(db, id_=user_id)
	if user_to_follow == current_user:
		error_response = ErrorResponse(
			loc="user_id",
			msg="You can not follow yourself",
			type="value_error"
		)
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=[error_response.model_dump()]
		)
	user_db = user.follow(db, user_db=current_user, user_to_follow=user_to_follow)
	return user_db


@router.post("/unfollow/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def unfollow(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_to_follow = user.get(db, id_=user_id)
	if user_to_follow == current_user:
		error_response = ErrorResponse(
			loc="user_id",
			msg="You can not follow yourself",
			type="value_error"
		)
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=[error_response.model_dump()]
		)
	user_db = user.unfollow(db, user_db=current_user, user_to_follow=user_to_follow)
	return user_db


@router.get("/get-followers/{user_id}", response_model=UserOutWithFollowers, status_code=status.HTTP_200_OK)
def get_followers(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	return user.get(db, id_=user_id)


@router.get("/get-followed/{user_id}", response_model=UserOutWithFollowed, status_code=status.HTTP_200_OK)
def get_followed(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	return user.get(db, id_=user_id)


@router.post("/uploadfile/", response_model=image.ImageDBOut, status_code=status.HTTP_201_CREATED)
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


@router.post("/uploadfiles/", response_model=image.ImagesDBOut, status_code=status.HTTP_201_CREATED)
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


@router.get("/image/{filename}", response_model=image.ImageOut, status_code=status.HTTP_200_OK)
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
	return {"filepath": url, "name": db_image.name}


@router.get("/images", response_model=image.ImagesOut, status_code=status.HTTP_200_OK)
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


@router.get("/image-download/{filename}", status_code=status.HTTP_200_OK)
def download_image(
		*,
		current_user: Annotated[Users, Depends(get_current_user)],
		filename: str
) -> FileResponse:
	filepath = image_exist_check(filename)
	return FileResponse(filepath)


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_db = user.get(db, id_=user_id)
	return user_db


