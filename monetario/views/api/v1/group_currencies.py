
import json

from flask import request
from flask_login import login_required
from flask_login import current_user

from monetario.models import db
from monetario.models import Group
from monetario.models import GroupCurrency

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/group_currencies/', methods=['GET'])
@login_required
@jsonify()
@collection(GroupCurrency)
def get_group_currencies():
    return (
        GroupCurrency.query
        .options(
            db.contains_eager(GroupCurrency.group),
        )
        .join(Group, Group.id == GroupCurrency.group_id)
        .filter(GroupCurrency.group_id == current_user.group_id)
    )


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['GET'])
@login_required
@jsonify()
def get_group_currency(group_currency_id):
    return (
        GroupCurrency.query
        .options(
            db.contains_eager(GroupCurrency.group),
        )
        .join(Group, Group.id == GroupCurrency.group_id)
        .filter(
            GroupCurrency.id == group_currency_id,
            GroupCurrency.group_id == current_user.group_id
        )
        .first_or_404()
    )


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_group_currency(group_currency_id):
    group_currency = GroupCurrency.query.filter(
        GroupCurrency.id == group_currency_id,
        GroupCurrency.group_id == current_user.group_id
    ).first_or_404()

    db.session.delete(group_currency)
    db.session.commit()

    return {}, 204


@bp.route('/group_currencies/', methods=['POST'])
@login_required
@jsonify()
def add_group_currency():
    group_currency_schema = GroupCurrency.from_json(json.loads(request.data.decode('utf-8')))

    if group_currency_schema.errors:
        return {'errors': group_currency_schema.errors}, 400

    group_currency = GroupCurrency(**group_currency_schema.data)
    group_currency.group_id = current_user.group_id

    db.session.add(group_currency)
    db.session.commit()

    return group_currency, 201


@bp.route('/group_currencies/<int:group_currency_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_group_currency(group_currency_id):
    group_currency = GroupCurrency.query.filter(
        GroupCurrency.id == group_currency_id,
        GroupCurrency.group_id == current_user.group_id
    ).first_or_404()

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
