from flask.ext.testing import TestCase

from monetario.app import create_app


class CurrencyTest(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def test_get_currency_english(self):
        response = self.client.get("/API/v1/currencies/")

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'UAE Dirham')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Zimbabwe Dollar')

        self.assertEqual(response.status_code, 200)

    def test_get_currency_russian(self):
        response = self.client.get("/API/v1/currencies/?language=ru")

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дирхам (ОАЭ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Доллар Зимбабве')

        self.assertEqual(response.status_code, 200)

    def test_get_currency_ukrainian(self):
        response = self.client.get("/API/v1/currencies/?language=uk")

        self.assertEqual(response.json['currencies'][0]['symbol'], 'AED')
        self.assertEqual(response.json['currencies'][0]['name'], 'Дірхам (ОАЕ)')

        self.assertEqual(response.json['currencies'][-1]['symbol'], 'ZWD')
        self.assertEqual(response.json['currencies'][-1]['name'], 'Долар Зімбабве')

        self.assertEqual(response.status_code, 200)
