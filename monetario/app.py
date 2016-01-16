
from flask import Flask

from .extensions import babel, mail, sentry, db, login_manager
from . import views
from .config import config

from monetario.models import User
from monetario.models import Token


def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    babel.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    sentry.init_app(app)
    login_manager.init_app(app)

    configure_views(app)

    return app


def configure_views(app):
    app.register_blueprint(views.api.bp, url_prefix='/API')
    app.register_blueprint(views.api.v1.bp, url_prefix='/API/v1')


@login_manager.request_loader
def load_user_from_request(request):
    token = request.headers.get('Authentication-Token')

    if token:
        token = Token.verify_auth_token(token)

        if token and token.user_id:
            return User.query.get(token.user_id)

    return None


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

