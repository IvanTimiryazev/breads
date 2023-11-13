from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.api_v1.api import api_router
from app.core.config import settings

app = FastAPI(title="Breads")

app.include_router(api_router, prefix=settings.API_V1_STR)
app.mount("/static", StaticFiles(directory="../static"), name="static")


@app.get("/health", include_in_schema=True, status_code=status.HTTP_200_OK)
async def health() -> JSONResponse:
	return JSONResponse({"message": "It worked!!"})


if __name__ == '__main__':
	import uvicorn
	uvicorn.run(app, host=settings.SERVER_HOST, port=settings.SERVER_PORT, log_level="debug")
