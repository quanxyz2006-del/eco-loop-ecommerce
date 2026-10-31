"""FastAPI application entry point for ECO-LOOP."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import engine
from app.schemas.response import ApiResponse
from app.api.v1.router import router as v1_router
from app.services.initialization import initialise_database

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGES_DIR = PROJECT_ROOT / "frontend" / "pages"
PUBLIC_DIR = PROJECT_ROOT / "frontend" / "public"


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create the local schema/demo data and release resources on shutdown."""
    initialise_database()
    yield
    engine.dispose()


app = FastAPI(
    title="ECO-LOOP API",
    description="API cho nền tảng thời trang tuần hoàn và tái thương mại ECO-LOOP.",
    version="1.0.0",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(v1_router, prefix=settings.api_prefix)
app.mount("/assets", StaticFiles(directory=PUBLIC_DIR), name="assets")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """Wrap application errors in the same envelope as successful responses."""
    detail = exc.detail if isinstance(exc.detail, str) else "Yêu cầu không thể xử lý."
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content=ApiResponse[dict[str, Any]](
            success=False,
            data=None,
            message=detail,
            errors=[{"status": exc.status_code, "detail": exc.detail}],
        ).model_dump(mode="json"),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return validation errors using the project's standard response shape."""
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    body = ApiResponse[dict[str, Any]](
        success=False, data=None, message="Dữ liệu đầu vào không hợp lệ.", errors=errors
    )
    if errors:
        details = "; ".join(f"{item['field']}: {item['message']}" for item in errors)
        body.message = f"{body.message} {details}"
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures and return a non-sensitive API error envelope."""
    logger.exception("Unhandled API exception", exc_info=exc)
    body = ApiResponse[dict[str, Any]](
        success=False,
        data=None,
        message="Đã xảy ra lỗi máy chủ.",
        errors=[{"type": "internal_server_error"}],
    )
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))


@app.get("/health", tags=["System"], response_model=ApiResponse[dict[str, str]])
def health_check() -> ApiResponse[dict[str, str]]:
    """Report application availability without requiring a database connection."""
    return ApiResponse(
        success=True,
        data={"status": "ok", "service": "eco-loop-api"},
        message="Dịch vụ đang hoạt động.",
    )


@app.get("/", include_in_schema=False)
def home_page() -> FileResponse:
    """Serve the storefront landing page."""
    return FileResponse(PAGES_DIR / "index.html")


@app.get("/admin", include_in_schema=False)
def admin_page() -> FileResponse:
    """Serve the separate administration portal."""
    return FileResponse(PAGES_DIR / "admin" / "index.html")


@app.get("/{page}.html", include_in_schema=False)
def static_page(page: str) -> FileResponse:
    """Serve only known storefront documents; never resolve arbitrary paths."""
    allowed_pages = {
        "about", "products", "product-detail", "trade-in", "cart", "checkout", "account",
        "news", "news-detail", "contact",
    }
    if page not in allowed_pages:
        raise HTTPException(status_code=404, detail="Không tìm thấy trang.")
    return FileResponse(PAGES_DIR / f"{page}.html")


@app.get(
    f"{settings.api_prefix}/health/database",
    tags=["System"],
    response_model=ApiResponse[dict[str, str]],
)
def database_health_check() -> ApiResponse[dict[str, str]]:
    """Check connectivity to the configured database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return JSONResponse(
            status_code=503,
            content=ApiResponse[dict[str, str]](
                success=False,
                data={"status": "unavailable"},
                message="Không thể kết nối cơ sở dữ liệu.",
                errors=[{"type": "database_unavailable"}],
            ).model_dump(mode="json"),
        )
    return ApiResponse(
        success=True,
        data={"status": "ok", "database": "connected"},
        message="Kết nối cơ sở dữ liệu thành công.",
    )
