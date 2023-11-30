import pytest
from typing import Generator

from sqlalchemy.orm import Session

from tests.other_tools import get_random_email, get_random_password
from tests.conftest import client, session
from app.schemas.users import UserCreate
from app.schemas.post import PostDBCreate
from app.crud.crud_user import user
from app.crud.crud_post import post
from app.models.users import Users


@pytest.fixture(scope="session")
def create_user(session: Session) -> Generator:
	email = get_random_email()
	password = get_random_password()
	user_in = UserCreate(email=email, password=password)
	user_obj = user.create(session, obj_in=user_in)
	yield user_obj


@pytest.fixture(scope="session")
def create_post(session: Session, create_user: Users):
	post_obj = PostDBCreate(content="test", user_id=create_user.id)
	db_post = post.create(session, obj_in=post_obj)
	yield db_post

