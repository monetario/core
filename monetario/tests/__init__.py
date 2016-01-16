from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db
from monetario.models import App
from monetario.models import Token


class BaseTestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def create_api_app(self, user, expires_in=60):
        app = App(name='Test API', user=user)
        app.secret = app.generate_auth_token(expires_in=expires_in)
        db.session.add(app)
        db.session.commit()
        return app

    def get_token(self, app, user):
        token = Token(app=app, user=user)

        db.session.add(token)
        db.session.commit()

        return token.generate_auth_token()
