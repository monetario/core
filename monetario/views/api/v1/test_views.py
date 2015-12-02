
from . import bp


@bp.route('/test/')
def test_endpoint():
    return "Wow fuck yeah"
