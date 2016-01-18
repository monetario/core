import json

from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class TokensTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        db.session.add(self.user)
        db.session.commit()

        self.api_app = self.create_api_app(self.user)
        self.api_app.generate_auth_token()

        self.token = self.get_token(self.api_app, self.user)

    def test_get_token_wrong_email(self):
        response = self.client.get(
            url_for('api.v1.get_token'),
            data=json.dumps({
                'email': self.user.email + '1',
                'password': '111',
                'secret': self.api_app.secret,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_get_token_wrong_password(self):
        response = self.client.get(
            url_for('api.v1.get_token'),
            data=json.dumps({
                'email': self.user.email,
                'password': '11111111111111',
                'secret': self.api_app.secret,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_get_token_wrong_secret(self):
        response = self.client.get(
            url_for('api.v1.get_token'),
            data=json.dumps({
                'email': self.user.email,
                'password': '111',
                'secret': self.api_app.secret + '1',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_get_token(self):
        response = self.client.get(url_for('api.v1.get_users'), content_type='application/json')

        self.assertEqual(response.status_code, 401)

        response = self.client.get(
            url_for('api.v1.get_token'),
            data=json.dumps({
                'email': self.user.email,
                'password': '111',
                'secret': self.api_app.secret,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('token', data)

        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': data['token']}
        )

        self.assertEqual(response.status_code, 200)

    def test_refresh_token_missed_token(self):
        response = self.client.put(
            url_for('api.v1.refresh_token'),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_token_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.refresh_token'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 400)

    def test_refresh_token(self):
        response = self.client.put(
            url_for('api.v1.refresh_token'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('token', data)
        self.assertNotEqual(data['token'], self.token)

    def test_delete_token_wrong_token(self):
        response = self.client.delete(
            url_for('api.v1.refresh_token'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_token(self):
        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.delete(
            url_for('api.v1.refresh_token'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            url_for('api.v1.get_users'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 401)
