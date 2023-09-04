import logging
from sqlalchemy.orm import Session

from app.crud.crud_user import user
from app.schemas.users import UserCreate
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
	if settings.FIRST_SUPERUSER:
		db_obj = user.get_by_email(db, email=settings.FIRST_SUPERUSER)
		if not db_obj:
			obj_in = UserAuth(email=settings.FIRST_SUPERUSER, password=settings.FIRST_SUPERUSER_PW)
			user.create(db, obj_in=obj_in)
		else:
			logger.warning(
				"User with this email already exists"
			)
	else:
		logger.warning(
			"FIRST_SUPERUSER needs to be provided as an env variable."
		)
