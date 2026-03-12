"""
Flask Application Factory
--------------------------
Implements the Application Factory Pattern for scalable, testable Flask apps.
"""

from flask import Flask
from .extensions import db, migrate, jwt, cache, limiter, cors, ma
from .middleware import register_middleware
from .api.v1 import api_v1_bp
from config import config_map


def create_app(config_name: str = "development") -> Flask:
    """
    Application factory function.

    Args:
        config_name: One of 'development', 'testing', 'production', 'staging'

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_map[config_name])

    # Initialize extensions
    _init_extensions(app)

    # Register middleware (CORS headers, request logging, error handlers)
    register_middleware(app)

    # Register blueprints
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    # Shell context for flask CLI
    @app.shell_context_processor
    def make_shell_context():
        from .models.user import User
        return {"db": db, "User": User}

    return app


def _init_extensions(app: Flask) -> None:
    """Initialize all Flask extensions with the app instance."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
    ma.init_app(app)
