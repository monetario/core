from flask import Blueprint

bp = Blueprint("api", __name__)


from . import discovery
from . import v1
