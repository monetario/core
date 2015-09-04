
from . import bp


@bp.route('/')
def test_endpoint():
    return "Wow it works"
