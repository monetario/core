from monetario.app import db

from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class SmokeTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_smoke(self):
        response = self.client.get(
            "/API/",
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)

        for version, urls in response.json['versions'].items():
            for url in urls.values():
                self.check_page(url)

    def check_page(self, url):
        response = self.client.get(
            url,
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )

        self.assertEqual(response.status_code, 200)
