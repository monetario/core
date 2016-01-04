
import json

from flask import request

from monetario.models import db
from monetario.models import User
from monetario.models import Record
from monetario.models import Account
from monetario.models import GroupCurrency
from monetario.models import GroupCategory

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/records/', methods=['GET'])
@jsonify()
@collection(Record)
def get_records():
    return Record.query


@bp.route('/records/<int:record_id>/', methods=['GET'])
@jsonify()
def get_record(record_id):
    record = Record.query.get_or_404(record_id)
    return record


@bp.route('/records/<int:record_id>/', methods=['DELETE'])
@jsonify()
def delete_record(record_id):
    record = Record.query.get_or_404(record_id)

    db.session.delete(record)
    db.session.commit()

    return {}, 204


@bp.route('/records/', methods=['POST'])
@jsonify()
def add_record():
    record_schema = Record.from_json(json.loads(request.data.decode('utf-8')))

    if record_schema.errors:
        return {'errors': record_schema.errors}, 400

    user = User.query.filter(User.id == record_schema.data['user_id']).first()

    if not user:
        return {'errors': {'user': 'User with this id does not exist'}}, 400

    account = Account.query.filter(Account.id == record_schema.data['account_id']).first()

    if not account:
        return {'errors': {'account': 'Account with this id does not exist'}}, 400

    category = GroupCategory.query.filter(
        GroupCategory.id == record_schema.data['category_id']
    ).first()

    if not category:
        return {'errors': {'category': 'GroupCategory with this id does not exist'}}, 400

    currency = GroupCurrency.query.filter(
        GroupCurrency.id == record_schema.data['currency_id']
    ).first()

    if not currency:
        return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    record = Record(**record_schema.data)
    db.session.add(record)
    db.session.commit()

    return record, 201


@bp.route('/records/<int:record_id>/', methods=['PUT'])
@jsonify()
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)

    record_schema = Record.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if record_schema.errors:
        return {'errors': record_schema.errors}, 400

    if 'user_id' in record_schema.data:
        user = User.query.filter(User.id == record_schema.data['user_id']).first()

        if not user:
            return {'errors': {'user': 'User with this id does not exist'}}, 400

    if 'account_id' in record_schema.data:
        account = Account.query.filter(Account.id == record_schema.data['account_id']).first()

        if not account:
            return {'errors': {'account': 'Account with this id does not exist'}}, 400

    if 'category_id' in record_schema.data:
        category = GroupCategory.query.filter(
            GroupCategory.id == record_schema.data['category_id']
        ).first()

        if not category:
            return {'errors': {'category': 'GroupCategory with this id does not exist'}}, 400

    if 'currency_id' in record_schema.data:
        currency = GroupCurrency.query.filter(
            GroupCurrency.id == record_schema.data['currency_id']
        ).first()

        if not currency:
            return {'errors': {'currency': 'Group currency with this id does not exist'}}, 400

    for field, value in record_schema.data.items():
        if hasattr(record, field):
            setattr(record, field, value)

    db.session.commit()

    return record, 200
