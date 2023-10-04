# from elasticsearch import Elasticsearch
# from app.core.config import settings
# from fastapi import Depends
# from typing import Annotated
# import logging
#
# from elasticsearch_dsl import connections, Document, Text, Date, Integer, Index
# from app.schemas.users import UserOut
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
#
# def get_es_client():
# 	"""DI for elasticsearch client"""
# 	es = ElasticSearchTest()
# 	try:
# 		yield es
# 	except Exception as e:
# 		logger.error(e)
#
#
# class User(Document):
# 	email = Text()
# 	name = Text()
# 	surname = Text()
# 	birth_date = Date()
# 	about_me = Text()
# 	id = Integer()
#
# 	class Index:
# 		name = "moscow"
# 		settings = {
# 			"number_of_shards": 2
# 		}
#
#
# # второй вариант как можно создавать индексы и документы (подойдет когда один индекс)
# my_index = Index('second_ind')
#
#
# @my_index.document
# class Post(Document):
# 	post = Text()
# 	author = Text()
#
#
# class ElasticSearchTest:
# 	def __init__(self):
# 		connections.create_connection(hosts=[settings.ELASTICSEARCH_URL], timeout=20)
#
# 	def index_user(self, user):
# 		logger.info("Saving user into Elastic")
# 		user_index = User(meta={"id": user.id})
# 		user_index.email = user.email
# 		user_index.name = user.name
# 		user_index.surname = user.surname
# 		user_index.birth_date = user.birth_date
# 		user_index.id = user.id
# 		user_index.save()
#
#
