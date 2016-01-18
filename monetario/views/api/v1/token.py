import json

from flask import request
from flask_login import login_required

from monetario.models import db
from monetario.models import App
from monetario.models import User
from monetario.models import Token

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify


@bp.route('/token/', methods=['GET'])
@jsonify()
def get_token():
    token_schema = Token.from_json(json.loads(request.data.decode('utf-8')))
    app = App.verify_auth_token(token_schema.data['secret'])

    if not app or app.secret != token_schema.data['secret']:
        return {}, 400

    user = User.query.filter_by(email=token_schema.data['email']).first()
    if user and user.verify_password(token_schema.data['password']):
        token = Token.query.filter(Token.app_id == app.id, Token.user_id == user.id).first()
        if not token:
            token = Token(app_id=app.id, user_id=user.id)

        db.session.add(token)
        db.session.commit()

        token.token = token.generate_auth_token()

        db.session.add(token)
        db.session.commit()

        return {'token': token.token}, 200

    return {}, 400


@bp.route('/token/', methods=['PUT'])
@jsonify()
def refresh_token():
    auth_token = request.headers.get('Authentication-Token')

    if auth_token:
        token = Token.query.filter(Token.token == auth_token).first()

        if token:
            token.token = token.generate_auth_token()

            db.session.add(token)
            db.session.commit()

            return {'token': token.token}, 200

    return {}, 400


@bp.route('/token/', methods=['DELETE'])
@login_required
@jsonify()
def revoke_token():
    auth_token = request.headers.get('Authentication-Token')
    if auth_token:
        token = Token.query.filter(Token.token == auth_token).first()

        token.token = None

        db.session.add(token)
        db.session.commit()

        return token, 200
    return {}, 400
