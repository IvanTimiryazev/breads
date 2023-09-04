from typing import Sequence, List, Optional, Dict
from datetime import date

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
	email: Optional[EmailStr] = None
	name: Optional[str] = None
	surname: Optional[str] = None
	birth_date: Optional[date] = None
	about_me: Optional[str] = None


class UserCreate(BaseModel):
	email: EmailStr
	password: str


class UserUpdate(UserBase):
	password: Optional[str]


class UserInDBBase(UserBase):
	id: Optional[int] = None

	class Config:
		orm_mode = True


class UserOut(UserInDBBase):
	pass


class UserInDB(UserInDBBase):
	hashed_password: str


class UserOutWithFollowings(UserOut):
	followers: Sequence[UserOut] | None = None
	followed: Sequence[UserOut] | None = None
