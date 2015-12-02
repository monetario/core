from . import bp
from .decorators import json
from .v1 import get_catalog as v1_catalog


@bp.route('/')
@json()
def get_discovery():
    return {'versions': {'v1': v1_catalog()}}
