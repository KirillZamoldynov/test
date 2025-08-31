from fastapi import APIRouter, status, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import AsyncSessionDep
from app.utils.logger import logger

router = APIRouter(tags=["health"])


@router.get("/live")
async def liveness():
    """Проверка того, что сервис запущен"""
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(db: AsyncSessionDep):
    """Проверка готовности сервиса к работе"""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except SQLAlchemyError as e:
        logger.error(f"База данных недоступна: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="База данных недоступна"
        )
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке готовности: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(db: AsyncSessionDep):
    """Общая проверка здоровья сервиса"""
    try:
        result = await db.execute(text("SELECT 1"))
        db_status = "healthy" if result else "unhealthy"

        return {
            "service": "healthy",
            "database": db_status
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка базы данных при проверке здоровья: {e}")
        return {
            "service": "healthy",
            "database": "unhealthy"
        }
    except Exception as e:
        logger.error(f"Неожиданная ошибка при проверке здоровья: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера"
        )