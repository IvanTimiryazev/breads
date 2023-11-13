from datetime import datetime
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form

from sqlalchemy.orm import Session

from app.schemas.post import PostCreate, PostUpdate, PostDBOut, PostDBCreate
from app.schemas.image import ImageDB
from app.schemas.exceptions import ErrorResponse
from app.api.deps import get_db, get_current_user
from app.models.users import Users
from app.models.image import Image
from app.models.post import Post
from app.utils.image_processing import image_processing
from app.crud.crud_post import post

router = APIRouter()


@router.post("/create", response_model=PostDBOut, status_code=status.HTTP_201_CREATED)
def create(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		files: Annotated[List[UploadFile], File()] = None,
		obj_in: PostCreate
) -> Any:
	post_obj = PostDBCreate(**obj_in.model_dump(), user_id=current_user.id)
	db_post = Post(**post_obj.model_dump())
	db.add(db_post)
	if files:
		for file in files:
			name = image_processing(file)
			image_obj = ImageDB(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
			db_image = Image(**image_obj.model_dump())
			db.add(db_image)
			db_post.images.append(db_image)
	db.commit()
	return db_post


@router.put("/update/{post_id}", response_model=PostDBOut, status_code=status.HTTP_200_OK)
def update(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		files: Annotated[List[UploadFile], File()] = None,
		obj_in: PostUpdate,
		post_id: int
) -> Any:
	db_post = post.get(db, id_=post_id)
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
	if files:
		for file in files:
			name = image_processing(file)
			image_obj = ImageDB(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
			db_image = Image(**image_obj.model_dump())
			db.add(db_image)
			db_post.images.append(db_image)
	db_post = post.update(db, db_obj=db_post, obj_in=obj_in)
	db.commit()
	return db_post





