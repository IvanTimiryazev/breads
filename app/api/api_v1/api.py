from fastapi import APIRouter

from app.api.api_v1.endpoints import user, login, search, post, image

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(login.router, tags=["login"])
api_router.include_router(search.router, tags=["search"])
api_router.include_router(post.router, prefix="/post", tags=["post"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
