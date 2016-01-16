from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from flask.ext.login import LoginManager


db = SQLAlchemy()
babel = Babel()
mail = Mail()
migrate = Migrate()
sentry = Sentry()
login_manager = LoginManager()
