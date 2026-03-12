"""
Response Helpers
----------------
Standardized JSON response format across the entire API.

Every response follows this envelope:
    {
        "success": bool,
        "data":    object | null,
        "error":   string | null,
        "meta":    object | null   (optional)
    }
"""

from flask import jsonify
from typing import Any


def success(data: Any = None, status: int = 200, meta: dict | None = None):
    """
    Return a successful JSON response.

    Args:
        data:   The payload to return.
        status: HTTP status code (default 200).
        meta:   Optional metadata (pagination info, etc).
    """
    body = {"success": True, "data": data, "error": None}
    if meta:
        body["meta"] = meta
    return jsonify(body), status


def error(message: str, status: int = 400, details: Any = None):
    """
    Return an error JSON response.

    Args:
        message: Human-readable error description.
        status:  HTTP status code (default 400).
        details: Optional structured error details.
    """
    body = {"success": False, "data": None, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status
