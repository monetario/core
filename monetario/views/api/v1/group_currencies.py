
import json

from flask import request

from monetario.models import db
from monetario.models import Group
from monetario.models import GroupCurrency

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/group_currencies/', methods=['GET'])
@jsonify()
@collection(GroupCurrency)
def get_group_currencies():
    return GroupCurrency.query


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['GET'])
@jsonify()
def get_group_currency(group_currency_id):
    group_currency = GroupCurrency.query.get_or_404(group_currency_id)
    return group_currency


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['DELETE'])
@jsonify()
def delete_group_currency(group_currency_id):
    group_currency = GroupCurrency.query.get_or_404(group_currency_id)

    db.session.delete(group_currency)
    db.session.commit()

    return {}, 204


@bp.route('/group_currencies/', methods=['POST'])
@jsonify()
def add_group_currency():
    group_currency_schema = GroupCurrency.from_json(json.loads(request.data.decode('utf-8')))

    if group_currency_schema.errors:
        return {'errors': group_currency_schema.errors}, 400

    group = Group.query.filter(
        Group.id == group_currency_schema.data['group_id']
    ).first()

    if not group:
        return {'errors': {'group': 'Group with this id does not exist'}}, 400

    group_currency = GroupCurrency(**group_currency_schema.data)
    db.session.add(group_currency)
    db.session.commit()

    return group_currency, 201


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['PUT'])
@jsonify()
def edit_group_currency(group_currency_id):
    group_currency = GroupCurrency.query.get_or_404(group_currency_id)

    group_currency_schema = GroupCurrency.from_json(json.loads(request.data.decode('utf-8')),
                                                    partial=True)

    if group_currency_schema.errors:
        return {'errors': group_currency_schema.errors}, 400

    if 'group_id' in group_currency_schema.data:
        group = Group.query.filter(
            Group.id == group_currency_schema.data['group_id']
        ).first()

        if not group:
            return {'errors': {'group': 'Group with this id does not exist'}}, 400

    for field, value in group_currency_schema.data.items():
        if hasattr(group_currency, field):
            setattr(group_currency, field, value)

    db.session.commit()

    return group_currency, 200
