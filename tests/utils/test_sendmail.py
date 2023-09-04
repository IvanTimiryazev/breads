from unittest.mock import patch, MagicMock
from pytest_mock import MockFixture
from pathlib import Path

from app.utils.sendmail import send_test_email, send_reset_password
from app.core.config import settings


@patch("app.utils.sendmail.send_email")
def test_send_test_email(mock_send_email: MagicMock) -> None:
	email_to = "princequincyy@gmail.com"
	project_name = settings.PROJECT_NAME
	subject = f"{project_name}: - test launch"
	with open(Path(settings.MAIL_TEMPLATES_DIR) / "test.html") as f:
		template_f = f.read()
	send_test_email(email_to)
	mock_send_email.assert_called_once_with(
		email_to=email_to,
		subject_template=subject,
		html_template=template_f,
		render_data={
			"user": "BELORUS"
		}
	)


def test_send_reset_password(mocker: MockFixture) -> None:
	mock_send_email = mocker.patch("app.utils.sendmail.send_email")
	email_to = "princequincyy@gmail.com"
	email = email_to
	token = 'qwerty'
	project_name = settings.PROJECT_NAME
	subject = f"{project_name} - Password recovery for user {email}"
	with open(Path(settings.MAIL_TEMPLATES_DIR) / "password_recovery.html") as f:
		template_f = f.read()
	link = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/reset-password?token={token}"
	send_reset_password(email_to=email_to, email=email, token=token)
	mock_send_email.assert_called_once_with(
		email_to=email_to,
		subject_template=subject,
		html_template=template_f,
		render_data={
			"user": email, "link": link
		}
	)

