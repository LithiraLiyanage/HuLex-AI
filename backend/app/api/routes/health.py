from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "HuLex AI API",
        "version": "0.1.0"
    }


@router.get("/health/database")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "connected",
            "database_name": "hulex_ai"
        }

    except Exception as error:
        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(error)
        }