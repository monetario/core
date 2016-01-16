
import gettext
import pycountry

from flask import request
from flask_login import login_required

from . import bp
from ..decorators import jsonify


@bp.route('/currencies/')
@login_required
@jsonify()
def get_currencies():
    def prepare_currency(currency):
        return {
            'symbol': currency.letter,
            'name': _(currency.name)
        }

    lang = request.args.get('language', 'en')
    try:
        language = gettext.translation('iso4217', pycountry.LOCALES_DIR, languages=[lang])
        language.install()
        _ = language.gettext
    except FileNotFoundError:
        _ = lambda x: x

    all_currencies = [prepare_currency(x) for x in pycountry.currencies.objects]
    return {'currencies': all_currencies}
