import os

from app.routes import bp as main_bp
from configs.config import BASE_DIR
from configs.logging import configure_logger, logger
from flask import Flask


def create_app():
    """Application factory"""
    # Configure logger first
    configure_logger()

    logger.info("Starting Credential Manager")
    logger.info(f"Data directory: {BASE_DIR}")

    # Create Flask app
    app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

    # Configuration
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod"),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Register blueprints
    app.register_blueprint(main_bp)

    # Health check endpoint
    @app.route("/health")
    def health():
        logger.debug("Health check endpoint called")
        return "OK", 200

    @app.before_first_request
    def startup_message():
        logger.success("Application startup complete")
        logger.info(f"Running in {'development' if app.debug else 'production'} mode")

    return app


if __name__ == "__main__":
    app = create_app()
    logger.debug(f"routes: {app.route}")
    try:
        logger.info("Starting development server on http://0.0.0.0:5000")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        raise
