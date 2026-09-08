import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.categories_routers import router as category_router
from app.api.routers.tasks_routers import router as task_router
from app.core.config import settings
from app.core.login import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=task_router)
app.include_router(router=category_router)

logger = logging.getLogger("app.middleware")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.GET_CORS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

request_count = 0


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    global request_count
    request_count += 1
    try:
        response: Response = await call_next(request)
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["x-request-number"] = str(request_count)
    return response
