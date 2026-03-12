"""
Health Check
------------
Lightweight endpoint used by load balancers, Docker health checks, and uptime monitors.
"""

from flask import jsonify, current_app
from app.extensions import db
from . import api_v1_bp


@api_v1_bp.get("/health")
def health():
    """
    GET /api/v1/health
    Returns service status and basic diagnostics.
    """
    db_ok = True
    try:
        db.session.execute(db.text("SELECT 1"))
    except Exception:
        db_ok = False

    status = "healthy" if db_ok else "degraded"
    code = 200 if db_ok else 503

    return jsonify({
        "status": status,
        "version": "1.0.0",
        "app": current_app.config["APP_NAME"],
        "checks": {
            "database": "ok" if db_ok else "error",
        },
    }), code
