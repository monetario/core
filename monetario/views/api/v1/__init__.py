from flask import Blueprint, jsonify, url_for

bp = Blueprint("api.v1", __name__)


def get_catalog():
    return {
        'currencies_url': url_for('api.v1.get_currencies', _external=True),
        'users_url': url_for('api.v1.get_users', _external=True),
    }


class ValidationError(ValueError):
    pass


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@bp.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


from . import auth
from . import test_views
from . import currency
from . import discovery
from . import users
from . import groups
from . import categories
from . import group_categories
from . import group_currencies
from . import accounts
from . import records
from . import apps
