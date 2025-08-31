import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.main import app as fastapi_app
from app.database import get_db, Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    """Создаем и удаляем таблицы для каждого теста"""
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Удаляем таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Сессия базы данных для тестов"""
    async with TestSessionLocal() as session:
        yield session


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Переопределение зависимости базы данных для тестов"""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для тестирования API"""
    # Явно указываем тип для app
    app: FastAPI = fastapi_app

    # Переопределяем зависимость базы данных
    app.dependency_overrides[get_db] = override_get_db

    # Используем ASGITransport для работы с FastAPI
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as test_client:
        yield test_client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()