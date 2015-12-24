import json

from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import UserFactory


class UsersTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()
        self.users = []
        self.users.extend(UserFactory.create_batch(30))
        for user in self.users:
            db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def test_create_new_user_missing_first_name(self):
        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'email': 'test@gmail.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('first_name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['first_name'])

    def test_create_new_user_missing_email(self):
        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'first_name': 'Ivan'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['email'])

    def test_create_new_user_missing_password(self):
        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'first_name': 'Ivan', 'email': 'ivan@gmail.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('password', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['password'])

    def test_create_new_user_incorrect_email(self):
        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'email': 'Ivanmail'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'email': 'ivan@gmailcom'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({'email': 'ivangmail.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

    def test_create_new_user(self):
        response = self.client.post(
            "/API/v1/users/",
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('email', data)
        self.assertEqual(data['email'], 'ivan@gmail.com')
        self.assertEqual(data['first_name'], 'Ivan')
        self.assertEqual(data['last_name'], 'Petrov')
        self.assertNotIn('password', data)

    def test_get_user(self):
        response = self.client.get(
            "/API/v1/users/",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['first_name'], self.users[0].first_name)
        self.assertEqual(data['last_name'], self.users[0].last_name)
        self.assertEqual(data['email'], self.users[0].email)
        self.assertEqual(data['active'], self.users[0].active)

    def test_get_users(self):
        per_page = 10
        response = self.client.get(
            "/API/v1/users/",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.users))
        self.assertEqual(data['meta']['pages'], len(self.users) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_users_five_per_page(self):
        per_page = 5
        response = self.client.get(
            "/API/v1/users/?per_page=%d" % per_page,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.users))
        self.assertEqual(data['meta']['pages'], len(self.users) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_users_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            "/API/v1/users/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.users))
        self.assertEqual(data['meta']['pages'], len(self.users) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_users_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            "/API/v1/users/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            "/API/v1/users/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            "/API/v1/users/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_users_sorting(self):
        per_page = 5
        page = 1
        sort = 'first_name,asc'

        response = self.client.get(
            "/API/v1/users/?expand=1&per_page=%d&page=%d&sort=%s" % (per_page, page, sort),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['first_name'] for x in data['objects']],
            [x.first_name for x in self.users[:5]]
        )

        sort = 'first_name,desc'
        response = self.client.get(
            "/API/v1/users/?expand=1&per_page=%d&page=%d&sort=%s" % (per_page, page, sort),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['first_name'] for x in data['objects']],
            sorted([x.first_name for x in self.users[-5:]], reverse=True)
        )
