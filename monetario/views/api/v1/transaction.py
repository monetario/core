
import json

from datetime import datetime

from flask import request
from flask_login import login_required
from flask_login import current_user

from monetario.models import db
from monetario.models import Account
from monetario.models import GroupCurrency
from monetario.models import Record
from monetario.models import Transaction
from monetario.models import User

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify


def make_transaction(user: User, source_account_id: int, target_account_id: int,
                     amount: float, currency_id: int, description: str,
                     date: datetime) -> Transaction:

    transaction = Transaction(
        amount=amount,
        currency_id=currency_id,
        source_account_id=source_account_id,
        target_account_id=target_account_id,
        user=user,
        date=date,
        description=description,
    )
    db.session.add(transaction)

    source_record = Record(
        amount=0 - amount if amount > 0 else amount,
        record_type=Record.RECORD_TYPE_EXPENSE,
        currency_id=currency_id,
        account_id=source_account_id,
        user=user,
        transaction=transaction,
        date=date,
        description=description,
    )
    db.session.add(source_record)

    target_record = Record(
        amount=0 - amount if amount < 0 else amount,
        record_type=Record.RECORD_TYPE_INCOME,
        currency_id=currency_id,
        account_id=target_account_id,
        user=user,
        transaction=transaction,
        date=date,
        description=description,
    )
    db.session.add(target_record)

    db.session.commit()

    return transaction


def update_transaction(transaction: Transaction, user: User, source_account_id: int,
                       target_account_id: int, amount: float, currency_id: int,
                       description: str, date: datetime) -> Transaction:

    transaction.amount = amount
    transaction.currency_id = currency_id
    transaction.source_account_id = source_account_id
    transaction.target_account_id = target_account_id
    transaction.user = user
    transaction.date = date
    transaction.description = description

    db.session.add(transaction)

    source_record = Record.query.filter(
        Record.record_type == Record.RECORD_TYPE_EXPENSE,
        Record.transaction_id == transaction.id,
        Record.user_id == user.id
    ).first()

    source_record.amount = 0 - amount if amount > 0 else amount
    source_record.currency_id = currency_id
    source_record.account_id = source_account_id
    source_record.date = date
    source_record.description = description

    db.session.add(source_record)

    target_record = Record.query.filter(
        Record.record_type == Record.RECORD_TYPE_INCOME,
        Record.transaction_id == transaction.id,
        Record.user_id == user.id
    ).first()

    target_record.amount = 0 - amount if amount < 0 else amount
    target_record.currency_id = currency_id
    target_record.account_id = target_account_id
    target_record.date = date
    target_record.description = description

    db.session.add(target_record)

    db.session.commit()

    return transaction


@bp.route('/transactions/<int:transaction_id>/', methods=['GET'])
@login_required
@jsonify()
def get_transaction(transaction_id):
    return (
        Transaction.query
        .options(
            db.contains_eager(Transaction.source_account),
            db.contains_eager(Transaction.target_account),
            db.contains_eager(Transaction.currency)
        )
        .join(Account, Account.id == Transaction.source_account_id, aliased=True)
        .join(Account, Account.id == Transaction.target_account_id, aliased=True)
        .join(GroupCurrency, GroupCurrency.id == Transaction.currency_id)
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first_or_404()
    )


@bp.route('/transactions/<int:transaction_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_transaction(transaction_id):
    transaction = (
        Transaction.query
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .first_or_404()
    )

    records = Record.query.filter(Record.transaction_id == transaction.id)

    for record in records:
        db.session.delete(record)

    db.session.delete(transaction)
    db.session.commit()

    return {}, 204


@bp.route('/transactions/', methods=['POST'])
@login_required
@jsonify()
def add_transaction():
    transaction_schema = Transaction.from_json(json.loads(request.data.decode('utf-8')))

    if transaction_schema.errors:
        return {'errors': transaction_schema.errors}, 400

    transaction_data = transaction_schema.data

    if transaction_data['source_account_id'] == transaction_data['target_account_id']:
        return {
            'errors': {'target_account': 'Source account and target account can not be equal'}
        }, 400

    source_account = Account.query.filter(
        Account.id == transaction_data['source_account_id']
    ).first()

    if not source_account:
        return {'errors': {'source_account': 'Source account with this id does not exist'}}, 400

    target_account = Account.query.filter(
        Account.id == transaction_data['target_account_id']
    ).first()

    if not target_account:
        return {'errors': {'target_account': 'Target account with this id does not exist'}}, 400

    currency = GroupCurrency.query.filter(
        GroupCurrency.id == transaction_data['currency_id']
    ).first()

    if not currency:
        return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    transaction = make_transaction(
        user=current_user,
        source_account_id=transaction_data['source_account_id'],
        target_account_id=transaction_data['target_account_id'],
        amount=transaction_data['amount'],
        currency_id=transaction_data['currency_id'],
        date=transaction_data.get('date'),
        description=transaction_data.get('description')
    )

    return transaction, 201


@bp.route('/transactions/<int:transaction_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_transaction(transaction_id):
    transaction = Transaction.query.filter(
        Transaction.id == transaction_id, Transaction.user_id == current_user.id
    ).first_or_404()

    transaction_schema = Transaction.from_json(
        json.loads(request.data.decode('utf-8')), partial=True
    )

    if transaction_schema.errors:
        return {'errors': transaction_schema.errors}, 400

    transaction_data = transaction_schema.data

    if transaction_data['source_account_id'] == transaction_data['target_account_id']:
        return {
           'errors': {'target_account': 'Source account and target account can not be equal'}
        }, 400

    source_account = Account.query.filter(
        Account.id == transaction_data['source_account_id']
    ).first()

    if not source_account:
        return {'errors': {'source_account': 'Source account with this id does not exist'}}, 400

    target_account = Account.query.filter(
        Account.id == transaction_data['target_account_id']
    ).first()

    if not target_account:
        return {'errors': {'target_account': 'Target account with this id does not exist'}}, 400

    if 'currency_id' in transaction_data:
        currency = GroupCurrency.query.filter(
            GroupCurrency.id == transaction_data['currency_id']
        ).first()

        if not currency:
            return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    transaction = update_transaction(
        transaction=transaction,
        user=current_user,
        source_account_id=transaction_data['source_account_id'],
        target_account_id=transaction_data['target_account_id'],
        amount=transaction_data['amount'],
        currency_id=transaction_data['currency_id'],
        date=transaction_data.get('date'),
        description=transaction_data.get('description'),
    )

    db.session.commit()

    return transaction, 200
