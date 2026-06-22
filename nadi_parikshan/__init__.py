from flask import Flask
from flask_cors import CORS

from .database import init_db
from .routes import main_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    init_db()
    app.register_blueprint(main_bp)

    return app
