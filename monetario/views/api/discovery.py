from . import bp
from .decorators import jsonify
from .v1 import get_catalog as v1_catalog


@bp.route('/')
@jsonify()
def get_discovery():
    return {'versions': {'v1': v1_catalog()}}
