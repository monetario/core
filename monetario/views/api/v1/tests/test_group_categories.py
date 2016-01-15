import json

from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupFactory
from monetario.views.api.v1.tests.fixtures import GroupCategoryFactory
from monetario.tests import BaseTestCase


class GroupCategoriesTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.group = GroupFactory.create()
        db.session.add(self.group)

        self.group_categories = GroupCategoryFactory.create_batch(30)
        for group_category in self.group_categories:
            db.session.add(group_category)

        db.session.commit()

    def test_create_new_group_category_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_group_category'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_group_category_wrong_parent(self):
        response = self.client.post(
            url_for('api.v1.add_group_category'),
            data=json.dumps({
                'name': 'Subgroup_category 1',
                'parent': self.group_categories[-1].id + 100,
                'group': self.group.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('parent', data['errors'])
        self.assertIn('Parent group_category with this id does not exist', data['errors']['parent'])

    def test_create_new_group_category_wrong_group(self):
        response = self.client.post(
            url_for('api.v1.add_group_category'),
            data=json.dumps({
                'name': 'Subgroup_category 1',
                'parent': self.group_categories[-1].id + 100,
                'group': self.group.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_create_new_group_category(self):
        response = self.client.post(
            url_for('api.v1.add_group_category'),
            data=json.dumps({
                'name': 'Smiths',
                'parent': self.group_categories[0].id,
                'group': self.group.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')
        self.assertEqual(data['parent']['id'], self.group_categories[0].id)
        self.assertEqual(data['parent']['name'], self.group_categories[0].name)

    def test_update_group_category_wrong_parent(self):
        response = self.client.put(
            url_for('api.v1.edit_group_category', group_category_id=self.group_categories[1].id),
            data=json.dumps({
                'name': 'Transport',
                'parent': self.group_categories[-1].id + 100,
                'group': self.group.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('parent', data['errors'])
        self.assertIn('Parent group_category with this id does not exist', data['errors']['parent'])

    def test_update_group_category_wrong_group(self):
        response = self.client.put(
            url_for('api.v1.edit_group_category', group_category_id=self.group_categories[1].id),
            data=json.dumps({
                'name': 'Transport',
                'parent': self.group_categories[-1].id,
                'group': self.group.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_update_group_category(self):
        response = self.client.put(
            url_for('api.v1.edit_group_category', group_category_id=self.group_categories[1].id),
            data=json.dumps({
                'name': 'Groceries',
                'parent': self.group_categories[0].id,
                'group': self.group.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Groceries')
        self.assertEqual(data['parent']['id'], self.group_categories[0].id)
        self.assertEqual(data['parent']['name'], self.group_categories[0].name)

    def test_delete_group_category(self):
        url = url_for('api.v1.delete_group_category', group_category_id=self.group_categories[0].id)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_get_group_category(self):
        response = self.client.get(
            url_for('api.v1.get_group_categories'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], self.group_categories[0].name)

    def test_get_group_categories(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_group_categories'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.group_categories))
        self.assertEqual(data['meta']['pages'], len(self.group_categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_categories_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_group_categories', per_page=per_page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.group_categories))
        self.assertEqual(data['meta']['pages'], len(self.group_categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_categories_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_group_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.group_categories))
        self.assertEqual(data['meta']['pages'], len(self.group_categories) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_categories_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_group_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_group_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_group_categories', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_group_categories_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for(
                'api.v1.get_group_categories', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.group_categories[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for(
                'api.v1.get_group_categories', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.group_categories[-5:]], reverse=True)
        )
