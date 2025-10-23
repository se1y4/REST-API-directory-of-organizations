from typing import Annotated, AsyncGenerator

from fastapi.security.api_key import APIKeyHeader
from fastapi import Depends, HTTPException, Security, status

from app.core.db import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_db)]


# API токен в Header
api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


# Проверка API токена
async def get_api_token(api_key: str = Security(api_key_header)):
    if api_key != settings.security.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return api_key