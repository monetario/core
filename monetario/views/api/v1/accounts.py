
import json

from flask import request

from monetario.models import db
from monetario.models import User
from monetario.models import Account
from monetario.models import GroupCurrency

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/accounts/', methods=['GET'])
@jsonify()
@collection(Account)
def get_accounts():
    return Account.query


@bp.route('/accounts/<int:account_id>/', methods=['GET'])
@jsonify()
def get_account(account_id):
    account = Account.query.get_or_404(account_id)
    return account


@bp.route('/accounts/<int:account_id>/', methods=['DELETE'])
@jsonify()
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)

    db.session.delete(account)
    db.session.commit()

    return {}, 204


@bp.route('/accounts/', methods=['POST'])
@jsonify()
def add_account():
    account_schema = Account.from_json(json.loads(request.data.decode('utf-8')))

    if account_schema.errors:
        return {'errors': account_schema.errors}, 400

    user = User.query.filter(User.id == account_schema.data['user_id']).first()

    if not user:
        return {'errors': {'user': 'User with this id does not exist'}}, 400

    currency = GroupCurrency.query.filter(
        GroupCurrency.id == account_schema.data['currency_id']
    ).first()

    if not currency:
        return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    account = Account(**account_schema.data)
    db.session.add(account)
    db.session.commit()

    return account, 201


@bp.route('/accounts/<int:account_id>/', methods=['PUT'])
@jsonify()
def edit_account(account_id):
    account = Account.query.get_or_404(account_id)

    account_schema = Account.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if account_schema.errors:
        return {'errors': account_schema.errors}, 400

    if 'user_id' in account_schema.data:
        user = User.query.filter(User.id == account_schema.data['user_id']).first()

        if not user:
            return {'errors': {'user': 'User with this id does not exist'}}, 400

    if 'currency_id' in account_schema.data:
        currency = GroupCurrency.query.filter(
            GroupCurrency.id == account_schema.data['currency_id']
        ).first()

        if not currency:
            return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    for field, value in account_schema.data.items():
        if hasattr(account, field):
            setattr(account, field, value)

    db.session.commit()

    return account, 200