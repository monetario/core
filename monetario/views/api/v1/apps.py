import os
import json
import binascii

from flask import request
from flask_login import login_required

from monetario.models import db
from monetario.models import App
from monetario.models import User

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/apps/', methods=['GET'])
@login_required
@jsonify()
@collection(App)
def get_apps():
    return App.query


@bp.route('/apps/<int:app_id>/', methods=['GET'])
@login_required
@jsonify()
def get_app(app_id):
    app = App.query.get_or_404(app_id)
    return app


@bp.route('/apps/<int:app_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_app(app_id):
    app = App.query.get_or_404(app_id)

    db.session.delete(app)
    db.session.commit()

    return {}, 204


@bp.route('/apps/', methods=['POST'])
@login_required
@jsonify()
def add_app():
    app_schema = App.from_json(json.loads(request.data.decode('utf-8')))

    if app_schema.errors:
        return {'errors': app_schema.errors}, 400

    user = User.query.filter(User.id == app_schema.data['user_id']).first()

    if not user:
        return {'errors': {'user': 'User with this id does not exist'}}, 400

    app = App(**app_schema.data)
    app.secret = app.generate_auth_token()
    db.session.add(app)
    db.session.commit()

    return app, 201


@bp.route('/apps/<int:app_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_app(app_id):
    app = App.query.get_or_404(app_id)

    app_schema = App.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if app_schema.errors:
        return {'errors': app_schema.errors}, 400

    if 'user_id' in app_schema.data:
        user = User.query.filter(User.id == app_schema.data['user_id']).first()

        if not user:
            return {'errors': {'user': 'User with this id does not exist'}}, 400

    for field, value in app_schema.data.items():
        if hasattr(app, field):
            setattr(app, field, value)

    db.session.commit()

    return app, 200


@bp.route('/apps/<int:app_id>/secret/', methods=['PUT'])
@login_required
@jsonify()
def generate_secret(app_id):
    app = App.query.get_or_404(app_id)

    app.secret = app.generate_auth_token()

    db.session.add(app)
    db.session.commit()

    return app, 200


@bp.route('/apps/<int:app_id>/secret/', methods=['DELETE'])
@login_required
@jsonify()
def revoke_secret(app_id):
    app = App.query.get_or_404(app_id)

    app.secret = None

    db.session.add(app)
    db.session.commit()

    return app, 200
