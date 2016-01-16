from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class CurrencyTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_get_currency_english_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_currencies'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )

        self.assertEqual(response.status_code, 401)

    def test_get_currency_english(self):
        response = self.client.get(
            url_for('api.v1.get_currencies'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'UAE Dirham')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Zimbabwe Dollar')

    def test_get_currency_russian(self):
        response = self.client.get(
            url_for('api.v1.get_currencies', language='ru'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дирхам (ОАЭ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Доллар Зимбабве')

    def test_get_currency_ukrainian(self):
        response = self.client.get(
            url_for('api.v1.get_currencies', language='uk'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дірхам (ОАЕ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Долар Зімбабве')
