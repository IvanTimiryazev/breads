from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.message import Message
from app.schemas.token import Token
from app.crud.crud_user import user
from app.core.security import (
	create_access_token, create_password_reset_token,
	verify_password_reset_token, create_refresh_token, verify_token
)
from app.utils.sendmail import send_reset_password


router = APIRouter()


@router.post("/login", response_model=Token)
def login(
		*,
		db: Annotated[Session, Depends(get_db)],
		form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
		response: Response
) -> Any:
	"""Авторизация пользователя и создания токена доступа для него"""
	user_db = user.authenticate(db, email=form_data.username, password=form_data.password)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"}
		)
	access_token = create_access_token(user_db.id)
	refresh_token = create_refresh_token(user_db.id)
	response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
	return {
		'access_token': access_token,
		'token_type': 'bearer'
	}


@router.post("/password-recovery/{email}", response_model=Message, status_code=status.HTTP_200_OK)
def recover_password(email: str, db: Annotated[Session, Depends(get_db)]) -> Any:
	"""Функция для отправки письма с линком внутри которого токен."""
	user_db = user.get_by_email(db, email=email)
	if not user_db:
		raise HTTPException(
			status_code=404,
			detail="The user with this email does not exist in the system."
		)
	password_reset_token = create_password_reset_token(email)
	send_reset_password.delay(
		email_to=email,
		email=email,
		token=password_reset_token)
	return {"msg": "Password recovery email sent"}


@router.post("/reset-password/", response_model=Message, status_code=status.HTTP_200_OK)
def reset_password(
		*,
		token: Annotated[str, Body(...)],
		new_password: Annotated[str, Body(...)],
		db: Annotated[Session, Depends(get_db)]
) -> Any:
	"""Функция для проверки токена и сохранения нового пароля"""
	email = verify_password_reset_token(token)
	if not email:
		raise HTTPException(status_code=400, detail="Invalid token")
	user_db = user.get_by_email(db, email=email)
	if not user_db:
		raise HTTPException(
			status_code=404,
			detail="The user with this email does not exist in the system."
		)
	user.update(db, db_obj=user_db, obj_in={"password": new_password})
	return {"msg": "Password updated successfully"}


@router.post("/refresh", response_model=Token, status_code=status.HTTP_201_CREATED)
def refresh_access_token(
		db: Annotated[Session, Depends(get_db)],
		response: Response,
		refresh_token: Annotated[str, Cookie(alias="refresh_token", include_in_schema=False)] = None
) -> dict:
	user_id = verify_token(refresh_token)
	user_db = user.get(db, id_=user_id)
	if not user_db:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
			headers={"WWW-Authenticate": "Bearer"}
		)
	access_token = create_access_token(user_db.id)
	return {
		'access_token': access_token,
		'token_type': 'bearer'
	}
