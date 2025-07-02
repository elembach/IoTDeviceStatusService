from flask import Flask
from app.routes import api_bp
from app.database import init_db, close_db
import os


# Creates Flask application and registers the Blueprint
# Allows for testing configuration to be taken in
def create_app(test_config=None):
    app = Flask(__name__)

    # If there is not testing configuration passed in, then set the default config with
    # Default database and default API key
    if test_config is None:
        app.config["API_KEY"] = os.getenv("API_KEY", "defaultkey")
        app.config["DATABASE"] = os.getenv("DATABASE", "database.db")
    else:
        # However, load the provided testing config if there is one
        app.config.update(test_config)

    # Initializes database
    with app.app_context():
        init_db()

    # Register the blueprint and close the app once it is done being used
    app.register_blueprint(api_bp)
    app.teardown_appcontext(close_db)

    return app