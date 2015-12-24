from . import bp
from . import get_catalog
from ..decorators import jsonify


@bp.route('/')
@jsonify()
def discovery():
    return get_catalog()
