from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import status

from starlette.requests import Request
from typing import Optional
from starlette.status import HTTP_401_UNAUTHORIZED
from fastapi.exceptions import HTTPException

from app.core.config import settings
from app.schemas.token import TokenData


def get_password_hash(password: str) -> str:
	"""С помощью метода класса CryptContext создаем хэш пароля"""
	return PWD_CONTEXT.hash(password)


def verify_password(*, password: str, hashed_password: str) -> bool:
	"""Верифицируем пароль."""
	return PWD_CONTEXT.verify(password, hashed_password)


def create_access_token(subject: int) -> str:
	"""Создание токена доступа. В тело токена зашивается user_id"""
	now = datetime.utcnow()
	expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	to_encode = {"exp": expire, "sub": str(subject), "type": "access_token"}
	encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, settings.JWT_ALGORITHM)
	return encoded_jwt


def create_refresh_token(subject: int) -> str:
	"""Создание refresh token. В тело токена зашивается user_id"""
	now = datetime.utcnow()
	expire = now + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
	to_encode = {"exp": expire, "sub": str(subject), "type": "refresh_token"}
	encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, settings.JWT_ALGORITHM)
	return encoded_jwt


def create_password_reset_token(email: str) -> str:
	"""Создание токена для восстановления пароля. В тело токена зашиваем имэйл"""
	now = datetime.utcnow()
	expire = now + timedelta(minutes=settings.RESET_PASSWORD_EXPIRE_MINUTES)
	to_encode = {"exp": expire, "sub": email, "nbf": now}
	encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, settings.JWT_ALGORITHM)
	return encoded_jwt


def verify_password_reset_token(token: str) -> str | None:
	"""Проверяем токен. На выходе получаем либо имэйл который был зашит в токен либо ничего"""
	try:
		decoded_token = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
		return decoded_token["sub"]
	except JWTError:
		return None


def verify_token(token: str) -> int:
	"""Проверяем токен. На выходе получаем либо id который был зашит в токен либо raise"""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"}
	)
	try:
		payload = jwt.decode(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
		user_id: str = payload.get("sub")
		if not user_id:
			raise credentials_exception
		token_data = TokenData(id=user_id)
		return token_data.id
	except JWTError:
		raise credentials_exception


class OAuth2PasswordCookieBearer(OAuth2PasswordBearer):
	"""Переопределил метод __call__ чтобы вытащить токен из кука а не из хэдэра, если access token будет в куках"""
	async def __call__(self, request: Request) -> Optional[str]:
		authorization = request.cookies.get("access_token")
		if not authorization:
			if self.auto_error:
				raise HTTPException(
					status_code=HTTP_401_UNAUTHORIZED,
					detail="Not authenticated",
					headers={"WWW-Authenticate": "Bearer"},
				)
		return authorization


PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")
