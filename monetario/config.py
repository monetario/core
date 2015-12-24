
import os


class Config(object):
    DEBUG = True
    SERVER_NAME = os.environ['SERVER_NAME']
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_EXPIRE_ON_COMMIT = False

    SLOW_DB_QUERY_TIME = '0.5'
    SQLALCHEMY_RECORD_QUERIES = True

    BABEL_DEFAULT_LOCALE = 'ru'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Kiev'

    @staticmethod
    def init_app(app):
        pass

    SQLALCHEMY_DATABASE_URI = os.environ['DB_URI']


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"


class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
