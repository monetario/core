
from flask import Flask

from .extensions import babel, mail, sentry, db
from .config import Config
from . import views


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    babel.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    sentry.init_app(app)

    configure_views(app)

    return app


def configure_views(app):
    app.register_blueprint(views.api_1_0.bp, url_prefix='/API/v1')
