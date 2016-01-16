
import json

from flask import request
from flask_login import login_required

from monetario.models import db
from monetario.models import Category

from monetario.views.api.v1 import bp
from monetario.views.api.decorators import jsonify
from monetario.views.api.decorators import collection


@bp.route('/categories/', methods=['GET'])
@login_required
@jsonify()
@collection(Category)
def get_categories():
    return Category.query


@bp.route('/categories/<int:category_id>/', methods=['GET'])
@login_required
@jsonify()
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return category


@bp.route('/categories/<int:category_id>/', methods=['DELETE'])
@login_required
@jsonify()
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    db.session.delete(category)
    db.session.commit()

    return {}, 204


@bp.route('/categories/', methods=['POST'])
@login_required
@jsonify()
def add_category():
    category_schema = Category.from_json(json.loads(request.data.decode('utf-8')))

    if category_schema.errors:
        return {'errors': category_schema.errors}, 400

    if 'parent_id' in category_schema.data:
        parent = Category.query.filter(Category.id == category_schema.data['parent_id']).first()
        if not parent:
            return {'errors': {'parent': 'Parent category with this id does not exist'}}, 400

    category = Category(**category_schema.data)
    db.session.add(category)
    db.session.commit()

    return category, 201


@bp.route('/categories/<int:category_id>/', methods=['PUT'])
@login_required
@jsonify()
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    category_schema = Category.from_json(json.loads(request.data.decode('utf-8')), partial=True)

    if category_schema.errors:
        return {'errors': category_schema.errors}, 400

    if 'parent_id' in category_schema.data:
        parent = Category.query.filter(Category.id == category_schema.data['parent_id']).first()
        if not parent:
            return {'errors': {'parent': 'Parent category with this id does not exist'}}, 400

    for field, value in category_schema.data.items():
        if hasattr(category, field):
            setattr(category, field, value)

    db.session.commit()

    return category, 200
