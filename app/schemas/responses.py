from pydantic import BaseModel


class SuccessResponse(BaseModel):
	success: str
