from fastapi import APIRouter, Depends

from app.api.routes import organizations, activities, buildings
from .deps import get_api_token

# Главный API роутер
api_router = APIRouter(
    dependencies=[
        # Зависимость для проверки токена API
        Depends(get_api_token)
    ]
)

# Добавление маршрутов из различных модулей
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(buildings.router, prefix="/buildings", tags=["buildings"])