from math import ceil
from typing import Dict

from fastapi import HTTPException, status

from app.schemas.exceptions import ErrorResponse


def page_dict(
		*,
		page: int,
		size: int,
		total_posts: int
) -> Dict[str, int]:
	"""Рассчитываем общее количество страниц, возвращаю словарь с ключами для модели"""
	pages = ceil(total_posts / size)
	if page > pages:
		error_response = ErrorResponse(
			loc="page",
			msg="Page number is greater than possible.",
			type="value_error"
		)
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=[error_response.model_dump()]
		)
	return {
		"total": total_posts,
		"page": page,
		"size": size,
		"pages": pages
	}
