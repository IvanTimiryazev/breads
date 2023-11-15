from datetime import datetime
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, Form

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas.post import PostCreate, PostUpdate, PostDBOut, PostDBCreate, PostDBUpdate, PostsDBOut
from app.schemas.image import ImageDB
from app.schemas.responses import SuccessResponse
from app.api.deps import get_db, get_current_user
from app.models.users import Users
from app.models.image import Image
from app.models.post import Post
from app.utils.image_processing import image_processing, image_delete
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
	post_obj = PostDBUpdate(**obj_in.model_dump(exclude_unset=True), updated_at=datetime.utcnow())
	db_post = post.get(db, id_=post_id)
	if files:
		for file in files:
			name = image_processing(file)
			image_obj = ImageDB(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
			db_image = Image(**image_obj.model_dump())
			db.add(db_image)
			db_post.images.append(db_image)
	db_post = post.update(db, db_obj=db_post, obj_in=post_obj)
	db.commit()
	return db_post


@router.delete("/{post_id}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def delete_post(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		post_id: int
) -> Any:
	db_post = post.get(db, id_=post_id)
	for image in db_post.images.all():
		image_delete(image.name)
	post.remove(db, id_=post_id)
	return {"success": "Post has been deleted."}


@router.delete("/{post_id}/image/{filename}", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
def delete_image_from_post(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		post_id: int,
		filename: str
) -> Any:
	image_delete(filename)
	db_image = db.execute(select(Image).filter_by(name=filename)).scalar_one_or_none()
	db_post = post.get(db, id_=post_id)
	db_post.images.remove(db_image)
	post_obj = PostDBUpdate(updated_at=datetime.utcnow())
	post.update(db, db_obj=db_post, obj_in=post_obj)
	return {"success": "Image has been deleted."}


@router.get("/get-all", response_model=PostsDBOut, status_code=status.HTTP_200_OK)
def get_posts(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	return {"posts": [p for p in current_user.posts.all()]}


@router.get("/{post_id}", response_model=PostDBOut, status_code=status.HTTP_200_OK)
def get_post(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		post_id: int
) -> Any:
	return post.get(db, id_=post_id)
