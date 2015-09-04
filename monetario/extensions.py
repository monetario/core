from flask.ext.babel import Babel
from flask.ext.mail import Mail
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry


db = SQLAlchemy()
babel = Babel()
mail = Mail()
migrate = Migrate()
sentry = Sentry()
