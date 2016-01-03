import json

from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupFactory


class GroupsTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()
        self.groups = []
        self.groups.extend(GroupFactory.create_batch(30))
        for group in self.groups:
            db.session.add(group)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def test_create_new_group_missing_name(self):
        response = self.client.post(
            "/API/v1/groups/",
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_group(self):
        response = self.client.post(
            "/API/v1/groups/",
            data=json.dumps({
                'name': 'Smiths',

            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')

    def test_get_group(self):
        response = self.client.get(
            "/API/v1/groups/",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], self.groups[0].name)

    def test_get_groups(self):
        per_page = 10
        response = self.client.get(
            "/API/v1/groups/",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.groups))
        self.assertEqual(data['meta']['pages'], len(self.groups) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_groups_five_per_page(self):
        per_page = 5
        response = self.client.get(
            "/API/v1/groups/?per_page=%d" % per_page,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.groups))
        self.assertEqual(data['meta']['pages'], len(self.groups) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_groups_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            "/API/v1/groups/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.groups))
        self.assertEqual(data['meta']['pages'], len(self.groups) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_groups_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            "/API/v1/groups/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            "/API/v1/groups/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            "/API/v1/groups/?per_page=%d&page=%d" % (per_page, page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_groups_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            "/API/v1/groups/?expand=1&per_page=%d&page=%d&sort=%s" % (per_page, page, sort),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.groups[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            "/API/v1/groups/?expand=1&per_page=%d&page=%d&sort=%s" % (per_page, page, sort),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.groups[-5:]], reverse=True)
        )
