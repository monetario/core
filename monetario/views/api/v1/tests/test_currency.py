from flask import url_for

from monetario.tests import BaseTestCase


class CurrencyTest(BaseTestCase):
    def test_get_currency_english(self):
        response = self.client.get(url_for('api.v1.get_currencies'))

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'UAE Dirham')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Zimbabwe Dollar')

        self.assertEqual(response.status_code, 200)

    def test_get_currency_russian(self):
        response = self.client.get(url_for('api.v1.get_currencies', language='ru'))

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дирхам (ОАЭ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Доллар Зимбабве')

        self.assertEqual(response.status_code, 200)

    def test_get_currency_ukrainian(self):
        response = self.client.get(url_for('api.v1.get_currencies', language='uk'))

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дірхам (ОАЕ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Долар Зімбабве')

        self.assertEqual(response.status_code, 200)
