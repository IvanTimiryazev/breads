from typing import Generator

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import registry

from app.core.config import settings
from app.db.base import Base
from app.main import app
from app.api.deps import get_db

Base: registry
test_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI_TEST)
TestSessionLocal = sessionmaker(autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def session() -> Generator:
	Base.metadata.drop_all(bind=test_engine)
	Base.metadata.create_all(bind=test_engine)

	_session = TestSessionLocal()
	try:
		yield _session
	finally:
		_session.close()


@pytest.fixture(scope="session")
def client(session) -> Generator:
	app.dependency_overrides[get_db] = lambda: session
	with TestClient(app) as c:
		yield c

