
from flask import Flask

from .extensions import babel, mail, sentry, db
from . import views
from .config import config


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    babel.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    sentry.init_app(app)

    configure_views(app)

    return app


def configure_views(app):
    app.register_blueprint(views.api.bp, url_prefix='/API')
    app.register_blueprint(views.api.v1.bp, url_prefix='/API/v1')
