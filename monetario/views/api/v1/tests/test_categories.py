import json

from flask import url_for
from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import CategoryFactory


class CategoriesTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()
        self.categories = []
        self.categories.extend(CategoryFactory.create_batch(30))
        for category in self.categories:
            db.session.add(category)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def test_create_new_category_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_category'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_category_wrong_parent(self):
        response = self.client.post(
            url_for('api.v1.add_category'),
            data=json.dumps({
                'name': 'Subcategory 1',
                'parent': self.categories[-1].id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('parent', data['errors'])
        self.assertIn('Parent category with this id does not exist', data['errors']['parent'])

    def test_create_new_category(self):
        response = self.client.post(
            url_for('api.v1.add_category'),
            data=json.dumps({
                'name': 'Smiths',
                'parent': self.categories[0].id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')
        self.assertEqual(data['parent']['id'], self.categories[0].id)
        self.assertEqual(data['parent']['name'], self.categories[0].name)

    def test_update_category_wrong_parent(self):
        response = self.client.put(
            url_for('api.v1.edit_category', category_id=self.categories[1].id),
            data=json.dumps({
                'name': 'Transport',
                'parent': self.categories[-1].id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('parent', data['errors'])
        self.assertIn('Parent category with this id does not exist', data['errors']['parent'])

    def test_update_category(self):
        response = self.client.put(
            url_for('api.v1.edit_category', category_id=self.categories[1].id),
            data=json.dumps({
                'name': 'Groceries',
                'parent': self.categories[0].id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Groceries')
        self.assertEqual(data['parent']['id'], self.categories[0].id)
        self.assertEqual(data['parent']['name'], self.categories[0].name)

    def test_delete_category(self):
        url = url_for('api.v1.delete_category', category_id=self.categories[0].id)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_get_category(self):
        response = self.client.get(
            url_for('api.v1.get_categories'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], self.categories[0].name)

    def test_get_categories(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_categories'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.categories))
        self.assertEqual(data['meta']['pages'], len(self.categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_categories_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.categories))
        self.assertEqual(data['meta']['pages'], len(self.categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_categories_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.categories))
        self.assertEqual(data['meta']['pages'], len(self.categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_categories_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_categories_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.categories[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for('api.v1.get_categories', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.categories[-5:]], reverse=True)
        )
