from flask.ext.testing import TestCase

from monetario.app import create_app


class SmokeTest(TestCase):
    def create_app(self):
        app = create_app()
        return app

    def test_smoke(self):
        response = self.client.get("/API/")

        self.assertEqual(response.status_code, 200)

        for version, urls in response.json['versions'].items():
            for url in urls.values():
                self.check_page(url)

    def check_page(self, url):
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
