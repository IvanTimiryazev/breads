from elasticsearch_dsl import (
	Integer,
	Text,
	Document,
	Date
)


class UserDoc(Document):
	email = Text()
	name = Text()
	surname = Text()
	birth_date = Date()
	about_me = Text()
	id = Integer()

	class Index:
		name = "users"
		settings = {
			"number_of_shards": 3
		}
