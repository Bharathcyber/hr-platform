
import os

import psycopg
from fastapi import APIRouter

router = APIRouter()

SERVICE_NAME = "HR Platform API"
SERVICE_VERSION = "0.1.0"


def check_database():
    """Check whether PostgreSQL is reachable."""
    database_url = os.getenv("DATABASE_URL", "")

    if not database_url:
        return "not_configured"

    # psycopg expects postgresql://, not postgresql+psycopg://
    database_url = database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    try:
        with psycopg.connect(database_url, connect_timeout=2) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return "healthy"
    except Exception:
        return "unavailable"


@router.get("/health", tags=["Health"])
def health_check():
    # Preserve the existing endpoint for compatibility.
    return {"status": "ok"}


@router.get("/api/v1/health", tags=["Health"])
def versioned_health_check():
    database_status = check_database()

    # Redis and a background worker are not configured in this project yet.
    checks = {
        "database": database_status,
        "redis": "not_configured",
        "worker": "not_configured",
    }

    all_healthy = all(status == "healthy" for status in checks.values())

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "ok" if all_healthy else "degraded",
        "checks": checks,
    }
