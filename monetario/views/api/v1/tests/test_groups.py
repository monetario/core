import json

from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class GroupsTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.groups = GroupFactory.create_batch(30)
        for group in self.groups:
            db.session.add(group)
        db.session.commit()

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_create_new_group_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_group'),
            data=json.dumps({}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_group_wrong_token(self):
        response = self.client.post(
            url_for('api.v1.add_group'),
            data=json.dumps({}),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_new_group(self):
        response = self.client.post(
            url_for('api.v1.add_group'),
            data=json.dumps({
                'name': 'Smiths',

            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')

    def test_update_group_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.edit_group', group_id=self.groups[0].id),
            data=json.dumps({
                'id': self.groups[0].id,
                'name': 'Work',
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_group(self):
        response = self.client.put(
            url_for('api.v1.edit_group', group_id=self.groups[0].id),
            data=json.dumps({
                'id': self.groups[0].id,
                'name': 'Work',
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Work')

    def test_delete_group_wrong_token(self):
        url = url_for('api.v1.delete_group', group_id=self.groups[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_group(self):
        url = url_for('api.v1.delete_group', group_id=self.groups[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_group_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_groups'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_group(self):
        response = self.client.get(
            url_for('api.v1.get_groups'),
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
        self.assertEqual(data['name'], self.groups[0].name)

    def test_get_groups_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_groups'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_groups(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_groups'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_groups', per_page=per_page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_groups', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
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
            url_for('api.v1.get_groups', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_groups', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_groups', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_groups_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for('api.v1.get_groups', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.groups[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for('api.v1.get_groups', per_page=per_page, page=page, sort=sort, expand=1),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.groups[-5:]], reverse=True)
        )
