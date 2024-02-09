from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.users import UserCreate, UserUpdate, UserOut, UserOutWithFollowers, UserOutWithFollowed
from app.schemas.exceptions import ErrorResponse
from app.models.users import Users
from app.crud.crud_user import user
from app.elastic.elastic_service import get_es, ElasticSearchService
from app.elastic.documents import UserDoc


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


@router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def get_user_by_id(
		user_id: int,
		*,
		db: Annotated[Session, Depends(get_db)],
		current_user: Annotated[Users, Depends(get_current_user)]
) -> Any:
	user_db = user.get(db, id_=user_id)
	return user_db


