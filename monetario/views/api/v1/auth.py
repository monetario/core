import json

from flask import request

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

    if not app:
        return {}, 401

    user = User.query.filter_by(email=token_schema.data['email']).first()
    if user and user.verify_password(token_schema.data['password']):
        token = Token.query.filter(Token.app_id == app.id, Token.user_id == user.id).first()
        if not token:
            token = Token(app_id=app.id, user_id=user.id)

        db.session.add(token)
        db.session.commit()

        return {'token': token.generate_auth_token()}, 200

    return {}, 401
