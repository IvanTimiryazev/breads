from typing import Any, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.users import UserCreate, UserUpdate, UserOut, UserOutWithFollowings
from app.schemas import image
from app.models.users import Users
from app.models.image import Image
from app.crud.crud_user import user
from app.elastic.elastic_service import get_es, ElasticSearchService
from app.elastic.documents import UserDoc
from app.utils.image_processing import image_processing


router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
		*,
		db: Annotated[Session, Depends(get_db)],
		obj_in: UserCreate,
		es: Annotated[ElasticSearchService, Depends(get_es(UserDoc))]
) -> Any:
	user_db = db.query(Users).filter_by(email=obj_in.email).first()
	if user_db:
		raise HTTPException(
			status_code=400,
			detail="The user with this email already exists in the system"
		)
	user_db = user.create(db, obj_in=obj_in)
	es.add_to_index(UserOut.from_orm(user_db))
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
	es.add_to_index(UserOut.from_orm(updated_user))
	return updated_user


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_db = user.get(db, id=user_id)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The user with this id does not exists"
		)
	return user_db


@router.post("/follow/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def follow(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	follower = user.get(db, id=user_id)
	if not follower:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The user with this id does not exists"
		)
	if follower == current_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="You can not follow yourself"
		)
	user_db = user.follow(db, user_db=current_user, follower=follower)
	return user_db


@router.post("/unfollow/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def unfollow(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	follower = user.get(db, id=user_id)
	if not follower:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The user with this id does not exists"
		)
	if follower == current_user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="You can not unfollow yourself"
		)
	user_db = user.unfollow(db, user_db=current_user, follower=follower)
	return user_db


@router.get("/get-followers/{user_id}", response_model=UserOutWithFollowings, status_code=status.HTTP_200_OK)
def get_followers(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_db = user.get(db, id=user_id)
	followers = user_db.followers.all()
	user_db = UserOutWithFollowings(
		id=user_db.id,
		email=user_db.email,
		name=user_db.name,
		surname=user_db.surname,
		birth_date=user_db.birth_date,
		about_me=user_db.about_me,
		followers=followers
	)
	return user_db


@router.get("/get-followed/{user_id}", response_model=UserOutWithFollowings, status_code=status.HTTP_200_OK)
def get_followed(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_db = user.get(db, id=user_id)
	followed = user_db.followed.all()
	user_db = UserOutWithFollowings(
		id=user_db.id,
		email=user_db.email,
		name=user_db.name,
		surname=user_db.surname,
		birth_date=user_db.birth_date,
		about_me=user_db.about_me,
		followed=followed
	)
	return user_db


@router.post("/uploadfile/", response_model=image.ImageOut, status_code=status.HTTP_201_CREATED)
def upload_image(
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)],
		file: Annotated[UploadFile, File(...)]
) -> Any:
	name = image_processing(file)
	image_obj = image.Image(name=name, upload_time=datetime.utcnow(), user_id=current_user.id)
	db_image = Image(**image_obj.dict())
	db.add(db_image)
	db.commit()
	return db_image


