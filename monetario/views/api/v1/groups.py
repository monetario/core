
import json

from flask import request

from monetario.models import db
from monetario.models import Group

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/groups/', methods=['GET'])
@jsonify()
@collection(Group)
def get_groups():
    return Group.query


@bp.route('/groups/<int:group_id>/', methods=['GET'])
@jsonify()
def get_group(group_id):
    group = Group.query.get_or_404(group_id)
    return group


@bp.route('/groups/<int:group_id>/', methods=['DELETE'])
@jsonify()
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    db.session.delete(group)
    db.session.commit()

    return {}, 204


@bp.route('/groups/', methods=['POST'])
@jsonify()
def add_group():
    group_schema = Group.from_json(json.loads(request.data.decode('utf-8')))

    if group_schema.errors:
        return {'errors': group_schema.errors}, 400

    group = Group(**group_schema.data)
    db.session.add(group)
    db.session.commit()

    return group, 201


@bp.route('/groups/<int:group_id>/', methods=['PUT'])
@jsonify()
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)

    group_schema = Group.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if group_schema.errors:
        return {'errors': group_schema.errors}, 400

    for field, value in group_schema.data.items():
        if hasattr(group, field):
            setattr(group, field, value)

    db.session.commit()

    return group, 200
