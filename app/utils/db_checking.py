import logging

from tenacity import before_log, after_log, stop_after_attempt, wait_fixed, retry
from sqlalchemy import text

from app.db.session import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 10
seconds = 5


@retry(
	stop=stop_after_attempt(max_tries),
	wait=wait_fixed(seconds),
	after=after_log(logger, logging.INFO),
	before=before_log(logger, logging.WARNING)
)
def init_db():
	try:
		db = SessionLocal()
		db.execute(text("SELECT 1"))
	except Exception as e:
		logger.info(e)
		raise e


def main():
	logger.info("Initializing service")
	init_db()
	logger.info("Service finished initializing")


if __name__ == '__main__':
	main()

