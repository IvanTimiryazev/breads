import logging
from typing import Any, Type
from pydantic import BaseModel

import elastic_transport

from elasticsearch_dsl import connections, Document, Search
from elasticsearch_dsl.query import MultiMatch


from app.core.config import settings
from app.elastic.documents import UserDoc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_es(document: Type[Document]):
	def _get_es():
		try:
			es = ElasticSearchService(document)
			yield es
		except Exception as e:
			logger.error(e)
	return _get_es


class ElasticSearchService:
	def __init__(self, document) -> None:
		connections.create_connection(hosts=[settings.ELASTICSEARCH_URL], timeout=20)
		self.doc = document
		self._search = Search(index=self.doc.Index.name)

	def add_to_index(self, obj: dict | BaseModel) -> None:
		logger.info("Saving user into Elastic...")
		if isinstance(obj, dict):
			obj_data = obj
		else:
			obj_data = obj.model_dump(exclude_unset=True)
		index: UserDoc = self.doc(meta={"id": obj_data["id"]})
		for field in obj_data:
			setattr(index, field, obj_data[field])
		try:
			index.save()
			logger.info("User saved into Elastic Search")
		except elastic_transport.ConnectionError as e:
			logger.error(e)

	def retrieve(self, text: str):
		search = self._build_search(text)
		try:
			result = search.execute()
			return result
		except Exception as e:
			logger.error(e)

	def _build_search(self, text: str) -> Search:
		_match = MultiMatch(query=text, fields=["*"])
		search = self._search.query(_match)
		return search









# from app.schemas.users import UserOut
#
# u = UserOut(email='ss@mail.ru', name='ddd', surname='hhh', id=7)
#
# if __name__ == '__main__':
# ge = get_es(UserDoc)()
# es = next(ge)
# h = es.retrieve("cat")
# print(h.__dict__)








