import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.core.config import settings
from app.schemas.users import UserUpdate
from app.crud.crud_user import user
from tests.other_tools import get_random_email, get_random_password
from tests.conftest import client, session


def test_create_user_new(client: TestClient) -> None:
	email = get_random_email()
	password = get_random_password()
	data = {"email": email, "password": password}
	response = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
	assert response.status_code == 201
	response_data = response.json()
	assert response_data["email"] == email
	assert "id" in response_data


@pytest.mark.parametrize(
	"update_data", [
		(
			{"email": "kek@mail.ru"}
		),
		(
			{
				"email": "lol@mail.ru", "name": "Ryan",
				"surname": "Gosling", "about_me": "PIMP", "birth_date": "1980-11-12"
			}
		)
	]
)
def test_update_user(client: TestClient, update_data, session) -> None:
	email = get_random_email()
	password = get_random_password()
	data = {"email": email, "password": password}
	response = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
	assert response.status_code == 201
	user_db = user.get_by_email(session, email=response.json()["email"])
	token = client.post(f"{settings.API_V1_STR}/login", data={"username": email, "password": password})
	token = token.json()["access_token"]
	headers = {"Authorization": f"Bearer {token}"}
	response = client.put(f"{settings.API_V1_STR}/users/update", json=update_data, headers=headers)
	assert response.status_code == 200
	response = response.json()
	for key, value in update_data.items():
		assert response[key] == value

