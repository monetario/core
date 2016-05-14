
import json

from flask import request
from flask_login import login_required
from flask_login import current_user

from monetario.models import db
from monetario.models import User
from monetario.models import Account
from monetario.models import GroupCurrency

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/accounts/', methods=['GET'])
@login_required
@jsonify()
@collection(Account)
def get_accounts():
    return (
        Account.query
        .options(
            db.contains_eager(Account.user),
            db.contains_eager(Account.currency),
        )
        .join(User, User.id == Account.user_id)
        .join(GroupCurrency, GroupCurrency.id == Account.currency_id)
        .filter(Account.user_id == current_user.id)
    )


@bp.route('/accounts/<int:account_id>/', methods=['GET'])
@login_required
@jsonify()
def get_account(account_id):
    return (
        Account.query
        .options(
            db.contains_eager(Account.user),
            db.contains_eager(Account.currency),
        )
        .join(User, User.id == Account.user_id)
        .join(GroupCurrency, GroupCurrency.id == Account.currency_id)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first_or_404()
    )


@bp.route('/accounts/<int:account_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_account(account_id):
    account = Account.query.filter(
        Account.id == account_id, Account.user_id == current_user.id
    ).first_or_404()

    db.session.delete(account)
    db.session.commit()

    return {}, 204


@bp.route('/accounts/', methods=['POST'])
@login_required
@jsonify()
def add_account():
    account_schema = Account.from_json(json.loads(request.data.decode('utf-8')))

    if account_schema.errors:
        return {'errors': account_schema.errors}, 400

    currency = GroupCurrency.query.filter(
        GroupCurrency.id == account_schema.data['currency_id']
    ).first()

    if not currency:
        return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    account = Account(**account_schema.data)
    account.user = current_user

    db.session.add(account)
    db.session.commit()

    return account, 201


@bp.route('/accounts/<int:account_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_account(account_id):
    account = Account.query.filter(
        Account.id == account_id, Account.user_id == current_user.id
    ).first_or_404()

    account_schema = Account.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if account_schema.errors:
        return {'errors': account_schema.errors}, 400

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
