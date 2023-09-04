import pytest
from app.core.security import (
	get_password_hash,
	verify_password,
	create_access_token,
	create_password_reset_token,
	verify_password_reset_token
)


def test_get_password_hash() -> None:
	res = get_password_hash("LOL")
	assert res


@pytest.mark.parametrize("data, result", [("Biba", "Biba"), ("Boba", "Boba"), ("Dva", "Dva")])
def test_verify_password(data: str, result: str) -> None:
	token = get_password_hash(data)
	assert verify_password(password=data, hashed_password=token)


def test_create_access_token() -> None:
	result = create_access_token(subject=10)
	assert result


def test_create_password_reset_token() -> None:
	result = create_password_reset_token(email="masterKebab@mail.ru")
	assert result


@pytest.mark.parametrize(
	"data, result", [
		("Murat@mail.ru", "Murat@mail.ru"),
		("Obama@rambler.ru", "Obama@rambler.ru"),
		("Statham@yahooyeyu.com", "Statham@yahooyeyu.com")
	]
)
def test_verify_password_reset_token(data: str, result: str) -> None:
	token = create_password_reset_token(email=data)
	res = verify_password_reset_token(token)
	assert res == result

