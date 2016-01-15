from monetario.tests import BaseTestCase


class SmokeTest(BaseTestCase):
    def test_smoke(self):
        response = self.client.get("/API/")

        self.assertEqual(response.status_code, 200)

        for version, urls in response.json['versions'].items():
            for url in urls.values():
                self.check_page(url)

    def check_page(self, url):
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
