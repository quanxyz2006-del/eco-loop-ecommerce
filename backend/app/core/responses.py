"""Helpers for the common API response envelope."""

from typing import Any


def success(data: Any, message: str = "Thành công.") -> dict[str, Any]:
    """Build a successful JSON envelope."""
    return {"success": True, "data": data, "message": message, "errors": None}
