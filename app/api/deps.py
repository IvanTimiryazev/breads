from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import oauth2_scheme
from app.core.security import verify_token
from app.models.users import Users
from app.core.config import settings
from app.schemas.token import TokenData
from app.crud.crud_user import user


def get_db() -> Generator:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_current_user(
	db: Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]
) -> Users | None:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"}
	)
	user_id = verify_token(token)
	current_user = user.get(db, id_=user_id)
	if not current_user:
		raise credentials_exception
	return current_user




