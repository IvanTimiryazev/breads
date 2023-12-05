import pytest

from sqlalchemy.orm import Session

from fastapi import HTTPException

from tests.conftest import client, session
from .conftest import create_user, create_post
from app.models.post import Post
from app.crud.crud_post import post


def test_get(session: Session, create_post: Post) -> None:
	new_post = create_post
	assert new_post

	db_post = post.get(session, id_=new_post.id)
	assert db_post


def test_get_exception(session: Session, create_post: Post) -> None:
	new_post = create_post
	with pytest.raises(HTTPException):
		db_post = post.get(session, id_=100)



