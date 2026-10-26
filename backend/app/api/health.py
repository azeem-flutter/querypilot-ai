import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.db.connection import check_connection

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> dict:
    """Liveness: process zinda hai. Dependencies check nahi karta."""
    return {"status": "ok"}


@router.get("/ready")
def ready(settings: Settings = Depends(get_settings)):
    """Readiness: zaroori config aur dependencies. Tafseel (host, keys) kabhi expose nahi."""
    checks = {"llm_configured": settings.llm_configured}
    try:
        info = check_connection()
        checks["database"] = info["db_user"].startswith("query_readonly")
    except Exception as e:  # noqa: BLE001
        logger.warning("readiness db check failed: %s", type(e).__name__)
        checks["database"] = False
    ok = all(checks.values())
    return JSONResponse({"status": "ready" if ok else "not_ready", "checks": checks},
                        status_code=200 if ok else 503)