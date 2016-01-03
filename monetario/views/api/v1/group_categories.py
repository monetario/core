
import json

from flask import request

from monetario.models import db
from monetario.models import Group
from monetario.models import GroupCategory

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/group_categories/', methods=['GET'])
@jsonify()
@collection(GroupCategory)
def get_group_categories():
    return GroupCategory.query


@bp.route('/group_categories/<int:group_category_id>/', methods=['GET'])
@jsonify()
def get_group_category(group_category_id):
    group_category = GroupCategory.query.get_or_404(group_category_id)
    return group_category


@bp.route('/group_categories/<int:group_category_id>/', methods=['DELETE'])
@jsonify()
def delete_group_category(group_category_id):
    group_category = GroupCategory.query.get_or_404(group_category_id)

    db.session.delete(group_category)
    db.session.commit()

    return {}, 204


@bp.route('/group_categories/', methods=['POST'])
@jsonify()
def add_group_category():
    group_category_schema = GroupCategory.from_json(json.loads(request.data.decode('utf-8')))

    if group_category_schema.errors:
        return {'errors': group_category_schema.errors}, 400

    group = Group.query.filter(
        Group.id == group_category_schema.data['group_id']
    ).first()

    if not group:
        return {'errors': {'group': 'Group with this id does not exist'}}, 400

    if 'parent_id' in group_category_schema.data:
        parent = GroupCategory.query.filter(
            GroupCategory.id == group_category_schema.data['parent_id']
        ).first()

        if not parent:
            return {'errors': {'parent': 'Parent group_category with this id does not exist'}}, 400

    group_category = GroupCategory(**group_category_schema.data)
    db.session.add(group_category)
    db.session.commit()

    return group_category, 201


@bp.route('/group_categories/<int:group_category_id>/', methods=['PUT'])
@jsonify()
def edit_group_category(group_category_id):
    group_category = GroupCategory.query.get_or_404(group_category_id)

    group_category_schema = GroupCategory.from_json(json.loads(request.data.decode('utf-8')),
                                                    partial=True)

    if group_category_schema.errors:
        return {'errors': group_category_schema.errors}, 400

    if 'group_id' in group_category_schema.data:
        group = Group.query.filter(
            Group.id == group_category_schema.data['group_id']
        ).first()

        if not group:
            return {'errors': {'group': 'Group with this id does not exist'}}, 400

    if 'parent_id' in group_category_schema.data:
        parent = GroupCategory.query.filter(
            GroupCategory.id == group_category_schema.data['parent_id']
        ).first()

        if not parent:
            return {'errors': {'parent': 'Parent group_category with this id does not exist'}}, 400

    for field, value in group_category_schema.data.items():
        if hasattr(group_category, field):
            setattr(group_category, field, value)

    db.session.commit()

    return group_category, 200
