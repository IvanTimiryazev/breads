from typing import Any, Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.users import Users
from app.elastic.elastic_service import get_es, ElasticSearchService
from app.elastic.documents import UserDoc


router = APIRouter()


@router.post("/search", status_code=status.HTTP_200_OK)
def search(
		*,
		text: str,
		current_user: Annotated[Users, Depends(get_current_user)],
		db: Annotated[Session, Depends(get_db)],
		es: Annotated[ElasticSearchService, Depends(get_es(UserDoc))]
) -> Any:
	res = es.retrieve(text)
	print(res.hits)
	return res.hits

