import json

from flask import url_for
from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.views.api.v1.tests.fixtures import AppFactory


class AppsTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.apps = sorted(AppFactory.create_batch(30), key=lambda x: x.name)
        for app in self.apps:
            db.session.add(app)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def test_create_new_app_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_app'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_app_wrong_user(self):
        response = self.client.post(
            url_for('api.v1.add_app'),
            data=json.dumps({
                'name': 'Subapp 1',
                'user': self.user.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_create_new_app(self):
        response = self.client.post(
            url_for('api.v1.add_app'),
            data=json.dumps({
                'name': 'Smiths',
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')

    def test_update_app_wrong_user(self):
        response = self.client.put(
            url_for('api.v1.edit_app', app_id=self.apps[1].id),
            data=json.dumps({
                'name': 'Transport',
                'user': self.user.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_update_app(self):
        response = self.client.put(
            url_for('api.v1.edit_app', app_id=self.apps[1].id),
            data=json.dumps({
                'name': 'Groceries',
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Groceries')

    def test_delete_app(self):
        url = url_for('api.v1.delete_app', app_id=self.apps[0].id)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_generate_secret(self):
        secret = self.apps[0].secret
        response = self.client.put(
            url_for('api.v1.generate_secret', app_id=self.apps[0].id),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('secret', data)
        self.assertNotEqual(data['secret'], secret)

    def test_revoke_secret(self):
        url = url_for('api.v1.revoke_secret', app_id=self.apps[0].id)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            url_for('api.v1.get_app', app_id=self.apps[0].id),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('secret', data)
        self.assertIsNone(data['secret'])

    def test_get_app(self):
        response = self.client.get(
            url_for('api.v1.get_apps'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        print('@' * 100, self.apps, data['objects'])
        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], self.apps[0].name)

    def test_get_apps(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_apps'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.apps))
        self.assertEqual(data['meta']['pages'], len(self.apps) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_apps_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_apps', per_page=per_page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.apps))
        self.assertEqual(data['meta']['pages'], len(self.apps) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_apps_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_apps', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.apps))
        self.assertEqual(data['meta']['pages'], len(self.apps) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_apps_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_apps', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_apps', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_apps', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_apps_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for(
                'api.v1.get_apps', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.apps[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for(
                'api.v1.get_apps', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.apps[-5:]], reverse=True)
        )
