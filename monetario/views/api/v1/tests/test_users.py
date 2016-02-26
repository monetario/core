import json

from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class UsersTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.group = GroupFactory.create()
        db.session.add(self.group)

        self.users = UserFactory.create_batch(30)
        for user in self.users:
            user.group = self.group
            db.session.add(user)

        db.session.commit()

        self.user = self.users[0]
        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_create_new_user_missing_first_name(self):
        response = self.client.post(
            url_for('api.v1.add_user'),
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
            url_for('api.v1.add_user'),
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
            url_for('api.v1.add_user'),
            data=json.dumps({'first_name': 'Ivan', 'email': 'ivan@gmail.com'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('password', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['password'])

    def test_create_new_missing_group(self):
        response = self.client.post(
            url_for('api.v1.add_user'),
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['group'])

    def test_create_new_incorrect_group(self):
        response = self.client.post(
            url_for('api.v1.add_user'),
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111',
                'group': self.group.id * 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_create_new_user_incorrect_email(self):
        response = self.client.post(
            url_for('api.v1.add_user'),
            data=json.dumps({'email': 'Ivanmail'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.post(
            url_for('api.v1.add_user'),
            data=json.dumps({'email': 'ivan@gmailcom'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.post(
            url_for('api.v1.add_user'),
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
            url_for('api.v1.add_user'),
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111',
                'group': self.group.id
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

    def test_update_incorrect_group(self):
        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111',
                'group': self.group.id * 1000
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_update_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({
                'first_name': 'Ivan',
                'last_name': 'Petrov',
                'email': 'ivan@gmail.com',
                'password': '111',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_user_incorrect_email(self):
        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({'email': 'Ivanmail'}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({'email': 'ivan@gmailcom'}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({'email': 'ivangmail.com'}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('Not a valid email address.', data['errors']['email'])

    def test_update_user(self):
        response = self.client.put(
            url_for('api.v1.edit_user', user_id=self.users[0].id),
            data=json.dumps({
                'first_name': 'Oleg',
                'last_name': 'Sidorov',
                'email': 'oleg.sidirov@gmail.com',
                'password': '111'
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('email', data)
        self.assertEqual(data['email'], 'oleg.sidirov@gmail.com')
        self.assertEqual(data['first_name'], 'Oleg')
        self.assertEqual(data['last_name'], 'Sidorov')
        self.assertNotIn('password', data)

    def test_delete_user_wrong_token(self):
        url = url_for('api.v1.delete_user', user_id=self.users[1].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_user(self):
        url = url_for('api.v1.delete_user', user_id=self.users[1].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_user_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_user(self):
        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['first_name'], self.users[0].first_name)
        self.assertEqual(data['last_name'], self.users[0].last_name)
        self.assertEqual(data['email'], self.users[0].email)
        self.assertEqual(data['active'], self.users[0].active)

    def test_get_users_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_users(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_users', per_page=per_page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_users', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_users', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_users', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_users', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_users_sorting(self):
        per_page = 5
        page = 1
        sort = 'first_name,asc'

        response = self.client.get(
            url_for('api.v1.get_users', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['first_name'] for x in data['objects']],
            [x.first_name for x in self.users[:5]]
        )

        sort = 'first_name,desc'
        response = self.client.get(
            url_for('api.v1.get_users', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['first_name'] for x in data['objects']],
            sorted([x.first_name for x in self.users[-5:]], reverse=True)
        )
