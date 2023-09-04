from typing import Generator, Annotated

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import oauth2_scheme
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
	try:
		payload = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
		user_id: str = payload.get("sub")
		if user_id is None:
			raise credentials_exception
		token_data = TokenData(id=user_id)
	except JWTError:
		raise credentials_exception
	current_user = user.get(db, id=token_data.id)
	if not current_user:
		raise credentials_exception
	return current_user




