"""
Application Entry Point
-----------------------
Runs the Flask development server.
For production, use a WSGI server (Gunicorn/uWSGI) instead:

    gunicorn "wsgi:app" --workers 4 --bind 0.0.0.0:8000
"""

import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
    )
