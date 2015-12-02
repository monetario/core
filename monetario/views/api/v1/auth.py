
from . import bp


@bp.route('/token')
def get_token():
    return "Wow auth token"
