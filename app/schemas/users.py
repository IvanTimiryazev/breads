from typing import List, Sequence
from datetime import date

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
	email: EmailStr | None = None
	name: str | None = None
	surname: str | None = None
	birth_date: date | None = None
	about_me: str | None = None


class UserCreate(BaseModel):
	email: EmailStr
	password: str


class UserUpdate(UserBase):
	password: str | None = None


class UserInDBBase(UserBase):
	model_config = ConfigDict(from_attributes=True)

	id: int | None = None


class UserOut(UserInDBBase):
	pass


class UserInDB(UserInDBBase):
	hashed_password: str


class UserOutWithFollowers(UserOut):
	followers: List[UserOut] | None = None


class UserOutWithFollowed(UserOut):
	followed: List[UserOut] | None = None
