
import calendar
import datetime

from flask import request
from flask_login import login_required
from sqlalchemy.sql import case
from sqlalchemy.sql import func

from monetario.models import db
from monetario.models import Record

from monetario.serializers import BalanceSchema
from monetario.serializers import DateRangeFilterSchema
from monetario.serializers import CashFlowSchema
from monetario.serializers import ExpenseSchema
from monetario.serializers import IncomeSchema

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
            case([(Record.record_type == Record.RECORD_TYPE_EXPENSE, Record.amount)], else_=0)
        ).label('expense'),
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
            'expense': amounts.expense,
            'date': amounts.date,
            'start_balance': current_balance.start_balance,
            'end_balance': current_balance.end_balance,
        }).data
    else:
        balance = balance_schema.dump({
            'cash_flow': 0,
            'income': 0,
            'expense': 0,
            'date': end_date,
            'start_balance': current_balance.start_balance,
            'end_balance': current_balance.end_balance,
        }).data

    return balance


@bp.route('/cash_flows/', methods=['GET'])
@login_required
@jsonify()
def get_cash_flows():
    date_range_filter_schema = DateRangeFilterSchema().load(request.args)
    if date_range_filter_schema.errors:
        return {'errors': date_range_filter_schema.errors}, 400

    cash_flow_schema = CashFlowSchema()

    amounts = db.session.query(
        func.sum(Record.amount).label("cash_flow"),
        func.sum(
            case([(Record.record_type == Record.RECORD_TYPE_INCOME, Record.amount)], else_=0)
        ).label('income'),
        func.sum(
            case([(Record.record_type == Record.RECORD_TYPE_EXPENSE, Record.amount)], else_=0)
        ).label('expense'),
        func.date_trunc('month', Record.date).label("date"),
    ).group_by(
        func.date_trunc('month', Record.date)
    ).order_by(
        func.date_trunc('month', Record.date)
    )

    if 'date_from' in date_range_filter_schema.data:
        amounts = amounts.filter(Record.date >= date_range_filter_schema.data['date_from'])

    if 'date_to' in date_range_filter_schema.data:
        amounts = amounts.filter(Record.date < date_range_filter_schema.data['date_to'])

    return {'objects': cash_flow_schema.dump(amounts, many=True).data}


@bp.route('/incomes/', methods=['GET'])
@login_required
@jsonify()
def get_incomes():
    date_range_filter_schema = DateRangeFilterSchema().load(request.args)

    if date_range_filter_schema.errors:
        return {'errors': date_range_filter_schema.errors}, 400

    income_schema = IncomeSchema()

    incomes = db.session.query(
        func.sum(Record.amount).label("amount"),
        Record.category_id
    ).filter(
        Record.record_type == Record.RECORD_TYPE_INCOME,
    ).group_by(
        Record.category_id
    )

    if 'date_from' in date_range_filter_schema.data:
        incomes = incomes.filter(Record.date >= date_range_filter_schema.data['date_from'])

    if 'date_to' in date_range_filter_schema.data:
        incomes = incomes.filter(Record.date < date_range_filter_schema.data['date_to'])

    return {'objects': income_schema.dump(incomes, many=True).data}


@bp.route('/expenses/', methods=['GET'])
@login_required
@jsonify()
def get_expenses():
    date_range_filter_schema = DateRangeFilterSchema().load(request.args)

    if date_range_filter_schema.errors:
        return {'errors': date_range_filter_schema.errors}, 400

    expense_schema = ExpenseSchema()

    expenses = db.session.query(
        func.sum(Record.amount).label("amount"),
        Record.category_id
    ).filter(
        Record.record_type == Record.RECORD_TYPE_EXPENSE,
    ).group_by(
        Record.category_id
    )

    if 'date_from' in date_range_filter_schema.data:
        expenses = expenses.filter(Record.date >= date_range_filter_schema.data['date_from'])

    if 'date_to' in date_range_filter_schema.data:
        expenses = expenses.filter(Record.date < date_range_filter_schema.data['date_to'])

    return {'objects': expense_schema.dump(expenses, many=True).data}
