"""
Middleware
----------
Global request/response hooks and error handlers registered on the Flask app.
"""

import time
import logging
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_middleware(app: Flask) -> None:
    """Attach all middleware and error handlers to the app."""

    # ── Request timing ────────────────────────────────────────────────────────
    @app.before_request
    def start_timer():
        g.start_time = time.perf_counter()

    @app.after_request
    def log_request(response):
        if hasattr(g, "start_time"):
            elapsed_ms = round((time.perf_counter() - g.start_time) * 1000, 2)
            logger.info(
                "%s %s → %s  (%s ms)",
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
            )
            response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
        return response

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request.", "data": None}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "Authentication required.", "data": None}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "Access denied.", "data": None}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": f"Resource not found: {request.path}", "data": None}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed.", "data": None}), 405

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"success": False, "error": "Rate limit exceeded. Please slow down.", "data": None}), 429

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled server error: %s", e)
        return jsonify({"success": False, "error": "Internal server error.", "data": None}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"success": False, "error": e.description, "data": None}), e.code
