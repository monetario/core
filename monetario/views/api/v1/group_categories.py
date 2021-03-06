
import json

from flask import request
from flask_login import login_required
from flask_login import current_user

from monetario.models import db
from monetario.models import Group
from monetario.models import GroupCategory

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/group_categories/', methods=['GET'])
@login_required
@jsonify()
@collection(GroupCategory)
def get_group_categories():
    return (
        GroupCategory.query
        .options(
            db.contains_eager(GroupCategory.group),
        )
        .join(Group, Group.id == GroupCategory.group_id)
        .filter(GroupCategory.group_id == current_user.group_id)
    )


@bp.route('/group_categories/<int:group_category_id>/', methods=['GET'])
@login_required
@jsonify()
def get_group_category(group_category_id):
    return (
        GroupCategory.query
        .options(
            db.contains_eager(GroupCategory.group),
        )
        .join(Group, Group.id == GroupCategory.group_id)
        .filter(
            GroupCategory.id == group_category_id,
            GroupCategory.group_id == current_user.group_id
        )
        .first_or_404()
    )


@bp.route('/group_categories/<int:group_category_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_group_category(group_category_id):
    group_category = GroupCategory.query.filter(
        GroupCategory.id == group_category_id, GroupCategory.group_id == current_user.group_id
    ).first_or_404()

    db.session.delete(group_category)
    db.session.commit()

    return {}, 204


@bp.route('/group_categories/', methods=['POST'])
@login_required
@jsonify()
def add_group_category():
    group_category_schema = GroupCategory.from_json(json.loads(request.data.decode('utf-8')))

    if group_category_schema.errors:
        return {'errors': group_category_schema.errors}, 400

    if 'parent_id' in group_category_schema.data:
        parent = GroupCategory.query.filter(
            GroupCategory.id == group_category_schema.data['parent_id']
        ).first()

        if not parent:
            return {'errors': {'parent': 'Parent group_category with this id does not exist'}}, 400

    group_category = GroupCategory(**group_category_schema.data)
    group_category.group = current_user.group

    db.session.add(group_category)
    db.session.commit()

    return group_category, 201


@bp.route('/group_categories/<int:group_category_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_group_category(group_category_id):
    group_category = GroupCategory.query.filter(
        GroupCategory.id == group_category_id, GroupCategory.group_id == current_user.group_id
    ).first_or_404()

    group_category_schema = GroupCategory.from_json(json.loads(request.data.decode('utf-8')),
                                                    partial=True)

    if group_category_schema.errors:
        return {'errors': group_category_schema.errors}, 400

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
