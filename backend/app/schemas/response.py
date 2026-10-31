"""Common JSON response envelope used by all API endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Consistent response shape for successful and failed API requests."""

    success: bool
    data: T | None = None
    message: str
    errors: list[dict[str, object]] | None = None

    model_config = ConfigDict(from_attributes=True)
