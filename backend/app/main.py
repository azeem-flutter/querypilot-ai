import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import health, queries
from app.core.logging import request_id_var, setup_logging
from app.db.connection import close_pool
from app.llm.errors import LLMError

logger = logging.getLogger("app")


def _error(request: Request, status: int, code: str, message: str, **extra) -> JSONResponse:
    body = {"request_id": getattr(request.state, "request_id", "-"), "error_code": code, "message": message}
    body.update(extra)
    return JSONResponse(body, status_code=status)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_pool()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="QueryPilot AI", version="0.2.0", lifespan=lifespan)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = uuid.uuid4().hex[:16]           # hamesha server-generated (client ki id par bharosa nahi)
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.info("%s %s -> %s in %dms", request.method, request.url.path, response.status_code,
                        (time.perf_counter() - start) * 1000)
            return response
        finally:
            request_id_var.reset(token)

    @app.exception_handler(LLMError)
    async def llm_error_handler(request: Request, exc: LLMError):
        logger.warning("LLM error: %s", exc.code)
        return _error(request, exc.http_status, exc.code, exc.public_message)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        # input wapas echo nahi karte; sirf kahan galti hai aur kya
        problems = [{"field": ".".join(str(p) for p in e["loc"][1:]), "problem": e["msg"]} for e in exc.errors()]
        return _error(request, 422, "invalid_request", "The request is not valid.", details=problems)

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        logger.exception("unhandled error")      # stack trace sirf server log mein, user ko nahi
        return _error(request, 500, "internal_error", "Something went wrong.")

    app.include_router(health.router)
    app.include_router(queries.router)
    return app


app = create_app()