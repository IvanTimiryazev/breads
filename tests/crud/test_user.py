from sqlalchemy.orm import Session
import pytest
from datetime import date

from tests.other_tools import get_random_email, get_random_password
from tests.conftest import client, session
from .conftest import create_user
from app.schemas.users import UserCreate, UserUpdate
from app.crud.crud_user import user
from app.core.security import verify_password
from app.models.users import Users


def test_create_user(session: Session, create_user: Users) -> None:
	assert create_user.email

	user_in_db = user.get_by_email(session, email=create_user.email)
	assert user_in_db.email == create_user.email


@pytest.mark.parametrize(
	"user_in_upd, result", [
		(
			UserUpdate(
				email='test@mail.ru',
				name='KEK',
				surname='LOL',
				birth_date=date(1999, 1, 1),
				about_me='This is fun'
			),
			'test@mail.ru'
		),
		(
			UserUpdate(
				email='lol@mail.ru',
				name='BUMER',
				surname='VANDAM',
				birth_date=date(2001, 1, 1),
				about_me='This is vandam'
			),
			'lol@mail.ru'
		)
	]
)
def test_update_user(session: Session, user_in_upd: UserUpdate, result: str) -> None:
	email = get_random_email()
	password = get_random_password()
	user_in = UserCreate(email=email, password=password)
	user_obj = user.create(session, obj_in=user_in)
	assert user_obj.email == email

	user_update = user.update(session, db_obj=user_obj, obj_in=user_in_upd)
	assert user_update.email == result
	user_in_db = user.get_by_email(session, email=user_in_upd.email)
	assert user_in_db


def test_update_password(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_in = UserCreate(email=email, password=password)
	user_obj = user.create(session, obj_in=user_in)
	assert user_obj.email == email

	user_in = UserUpdate(password="qwerty")
	user_obj = user.update(session, db_obj=user_obj, obj_in=user_in)
	password = "qwerty"
	assert verify_password(password=password, hashed_password=user_obj.hashed_password)


def test_authenticate_user(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_obj = user.create(session, obj_in=UserCreate(email=email, password=password))
	user_in_db = user.authenticate(session, email=user_obj.email, password=password)
	assert user_in_db
	assert user_in_db.email == email


def test_non_authenticate_user(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_obj = user.create(session, obj_in=UserCreate(email=email, password=password))
	user_in_db = user.authenticate(session, email=user_obj.email, password=get_random_password())
	assert not user_in_db


def test_get_user(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_obj = user.create(session, obj_in=UserCreate(email=email, password=password))
	assert user_obj
	user_in_db = user.get(session, id_=user_obj.id)
	assert user_in_db
	assert user_in_db.email == email


def test_get_user_by_email(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_obj = user.create(session, obj_in=UserCreate(email=email, password=password))
	assert user_obj
	user_in_db = user.get_by_email(session, email=email)
	assert user_in_db.email == email


def test_remove_user(session: Session) -> None:
	email = get_random_email()
	password = get_random_password()
	user_obj = user.create(session, obj_in=UserCreate(email=email, password=password))
	assert user_obj
	user_in_db = user.get(session, id_=user_obj.id)
	assert user_in_db
	user_in_db = user.remove(session, id_=user_in_db.id)
	assert user_in_db.email == email
	user_in_db = user.get_by_email(session, email=user_in_db.email)
	assert not user_in_db


def test_follow(session: Session) -> None:
	email_1 = get_random_email()
	password_1 = get_random_password()
	email_2 = get_random_email()
	password_2 = get_random_password()
	user_in_1 = UserCreate(email=email_1, password=password_1)
	user_in_2 = UserCreate(email=email_2, password=password_2)
	user_1 = user.create(session, obj_in=user_in_1)
	user_2 = user.create(session, obj_in=user_in_2)
	assert user_1 and user_2
	assert not user.is_following(user_db=user_1, user_to_follow=user_2)
	user.follow(session, user_db=user_1, user_to_follow=user_2)
	assert user.is_following(user_db=user_1, user_to_follow=user_2)
	assert user_2 in user_1.followed.all()
	assert user_1 in user_2.followers.all()


def test_unfollow(session: Session) -> None:
	email_1 = get_random_email()
	password_1 = get_random_password()
	email_2 = get_random_email()
	password_2 = get_random_password()
	user_in_1 = UserCreate(email=email_1, password=password_1)
	user_in_2 = UserCreate(email=email_2, password=password_2)
	user_1 = user.create(session, obj_in=user_in_1)
	user_2 = user.create(session, obj_in=user_in_2)
	assert user_1 and user_2
	assert not user.is_following(user_db=user_2, user_to_follow=user_1)
	user.follow(session, user_db=user_2, user_to_follow=user_1)
	assert user.is_following(user_db=user_2, user_to_follow=user_1)
	user.unfollow(session, user_db=user_2, user_to_follow=user_1)
	assert not user.is_following(user_db=user_2, user_to_follow=user_1)
	assert user_1 not in user_2.followed.all()

