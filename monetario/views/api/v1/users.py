
import json

from flask import request
from flask_login import login_required

from monetario.models import db
from monetario.models import Group
from monetario.models import User

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/users/', methods=['GET'])
@login_required
@jsonify()
@collection(User)
def get_users():
    return (
        User.query
        .options(db.contains_eager(User.group))
        .join(Group, Group.id == User.group_id)
    )


@bp.route('/users/<int:user_id>/', methods=['GET'])
@login_required
@jsonify()
def get_user(user_id):
    return (
        User.query
        .options(db.contains_eager(User.group))
        .join(Group, Group.id == User.group_id)
        .filter(User.id == user_id)
        .first_or_404()
    )


@bp.route('/users/<int:user_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return {}, 204


@bp.route('/users/', methods=['POST'])
@jsonify()
def add_user():
    user_schema = User.from_json(json.loads(request.data.decode('utf-8')))

    if user_schema.errors:
        return {'errors': user_schema.errors}, 400

    group = Group.query.filter(Group.id == user_schema.data['group_id']).first()
    if not group:
        return {'errors': {'group': 'Group with this id does not exist'}}, 400

    email_duplicate_user = User.query.filter(User.email == user_schema.data['email']).first()

    if email_duplicate_user:
        return {'errors': {'email': 'User with this email is already exists'}}, 400

    user = User(**user_schema.data)
    db.session.add(user)
    db.session.commit()

    return user, 201


@bp.route('/users/<int:user_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    user_schema = User.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if user_schema.errors:
        return {'errors': user_schema.errors}, 400

    if 'group_id' in user_schema.data:
        group = Group.query.filter(Group.id == user_schema.data['group_id']).first()
        if not group:
            return {'errors': {'group': 'Group with this id does not exist'}}, 400

    if 'email' in user_schema.data:
        email_duplicate_user = User.query.filter(User.email == user_schema.data['email']).first()

        if email_duplicate_user:
            return {'errors': {'email': 'User with this email is already exists'}}, 400

    for field, value in user_schema.data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.session.commit()

    return user, 200
