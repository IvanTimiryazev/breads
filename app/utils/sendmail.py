import logging
import emails
from pathlib import Path
from emails.template import JinjaTemplate
from typing import Dict, Any

from app.core.config import settings


def send_email(
		*,
		email_to: str,
		subject_template: str,
		html_template: str,
		render_data: Dict[str, Any]
) -> None:
	message = emails.Message(
		subject=JinjaTemplate(subject_template),
		html=JinjaTemplate(html_template),
		mail_from=(settings.MAIL_FROM)
	)
	smpt_options = {
		"host": settings.MAIL_HOST, "port": settings.MAIL_PORT,
		"tls": settings.MAIL_USE_TLS, "password": settings.MAIL_PASSWORD,
		"user": settings.MAIL_USERNAME
	}
	response = message.send(to=email_to, render=render_data, smtp=smpt_options)
	logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
	project_name = settings.PROJECT_NAME
	subject = f"{project_name}: - test launch"
	with open(Path(settings.MAIL_TEMPLATES_DIR) / "test.html") as f:
		template_f = f.read()
	send_email(
		email_to=email_to,
		subject_template=subject,
		html_template=template_f,
		render_data={
			"user": "BELORUS"
		}
	)


def send_reset_password(*, email_to: str, email: str, token: str) -> None:
	project_name = settings.PROJECT_NAME
	subject = f"{project_name} - Password recovery for user {email}"
	with open(Path(settings.MAIL_TEMPLATES_DIR) / "password_recovery.html") as f:
		template_f = f.read()
	link = f"{settings.SERVER_HOST}:{settings.SERVER_PORT}/reset-password?token={token}"
	send_email(
		email_to=email_to,
		subject_template=subject,
		html_template=template_f,
		render_data={
			"user": email, "link": link
		}
	)
