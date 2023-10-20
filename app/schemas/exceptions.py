from pydantic import BaseModel


class ErrorResponse(BaseModel):
	loc: str
	msg: str
	type: str
