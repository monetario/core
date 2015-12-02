from . import bp
from . import get_catalog
from ..decorators import json


@bp.route('/')
@json()
def discovery():
    return get_catalog()
