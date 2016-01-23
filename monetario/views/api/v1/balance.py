
import calendar
import datetime

from flask_login import login_required
from sqlalchemy.sql import case
from sqlalchemy.sql import func

from monetario.models import db
from monetario.models import Record

from monetario.serializers import BalanceSchema

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify


@bp.route('/balance/<int:year>/<int:month>/', methods=['GET'])
@login_required
@jsonify()
def get_balance(year, month):
    (_, day) = calendar.monthrange(year, month)
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, day)
    balance_schema = BalanceSchema()

    amounts = db.session.query(
        func.sum(Record.amount).label("cash_flow"),
        func.sum(
            case([(Record.record_type == Record.RECORD_TYPE_INCOME, Record.amount)], else_=0)
        ).label('income'),
        func.sum(
            case([(Record.record_type == Record.RECORD_TYPE_OUTCOME, Record.amount)], else_=0)
        ).label('outcome'),
        func.date_trunc('month', Record.date).label("date"),
    ).filter(
        func.extract('year', Record.date) == year,
        func.extract('month', Record.date) == month,
    ).group_by(
        func.date_trunc('month', Record.date)
    ).first()

    current_balance = db.session.query(
        func.sum(
            case([(Record.date < start_date, Record.amount)], else_=0)
        ).label('start_balance'),
        func.sum(Record.amount).label("end_balance")
    ).filter(
        Record.date <= end_date
    ).first()

    if amounts:
        balance = balance_schema.dump({
            'cash_flow': amounts.cash_flow,
            'income': amounts.income,
            'outcome': amounts.outcome,
            'date': amounts.date,
            'start_balance': current_balance.start_balance,
            'end_balance': current_balance.end_balance,
        }).data
    else:
        balance = balance_schema.dump({
            'date': end_date,
            'start_balance': current_balance.start_balance,
            'end_balance': current_balance.end_balance,
        }).data

    return balance
