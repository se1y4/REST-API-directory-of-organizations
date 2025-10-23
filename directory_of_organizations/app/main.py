from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings

DEBUG = settings.DEBUG


api_description = """
Directory of Organizations API
API позволяет управлять деятельностями в городской информационной системе.
Доступны следующие операции:
- Получение списка всех организаций находящихся в конкретном здании
- Получение списка всех организаций, которые относятся к указанному виду деятельности
- Получение списка организаций, которые находятся в заданном радиусе/прямоугольной области относительно указанной точки на карте
- Получение информации об организации по её идентификатору
- Поиск организаций по виду деятельности
- Поиск организации по названию
"""

API_PREFIX = settings.service.API_PREFIX
OPENAPI_URL = f"{API_PREFIX}/openapi.json" if DEBUG else None
DOCS_URL = f"{API_PREFIX}/docs" if DEBUG else None
REDOC_URL = f"{API_PREFIX}/redocs" if DEBUG else None

app = FastAPI(
    title="Directory of Organizations API",
    description=api_description,
    openapi_url=OPENAPI_URL,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
)

app.include_router(api_router, prefix=settings.service.API_PREFIX)