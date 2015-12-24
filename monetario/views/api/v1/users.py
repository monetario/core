
import json

from flask import request

from monetario.models import db
from monetario.models import User

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/users/', methods=['GET'])
@jsonify()
@collection(User)
def get_users():
    return User.query


@bp.route('/users/<int:user_id>/', methods=['GET'])
@jsonify()
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return user


@bp.route('/users/<int:user_id>/', methods=['DELETE'])
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

    email_duplicate_user = User.query.filter(User.email == user_schema.data['email']).first()

    if email_duplicate_user:
        return {'errors': {'email': 'User with this email is already exists'}}, 400

    user = User(**user_schema.data)
    db.session.add(user)
    db.session.commit()

    return user, 201


@bp.route('/users/<int:user_id>/', methods=['PUT'])
@jsonify()
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    user_schema = User.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if user_schema.errors:
        return {'errors': user_schema.errors}, 400

    if 'email' in user_schema.data:
        email_duplicate_user = User.query.filter(User.email == user_schema.data['email']).first()

        if email_duplicate_user:
            return {'errors': {'email': 'User with this email is already exists'}}, 400

    for field, value in user_schema.data.items():
        if hasattr(user, field):
            setattr(user, field, value)

    db.session.commit()

    return user, 200