import json

from flask import url_for
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupFactory
from monetario.views.api.v1.tests.fixtures import GroupCurrencyFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.tests import BaseTestCase


class GroupCurrenciesTest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.group = GroupFactory.create()
        db.session.add(self.group)

        self.group_currencies = sorted(GroupCurrencyFactory.create_batch(30), key=lambda x: x.name)
        for group_currency in self.group_currencies:
            db.session.add(group_currency)

        db.session.commit()

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_create_new_group_currency_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_group_currency'),
            data=json.dumps({}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_group_currency_wrong_symbol(self):
        response = self.client.post(
            url_for('api.v1.add_group_currency'),
            data=json.dumps({
                'name': 'Subgroup_currency 1',
                'symbol': 'AAA',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('symbol', data['errors'])
        self.assertIn('Symbol is not valid', data['errors']['symbol'])

    def test_create_new_group_currency_wrong_group(self):
        response = self.client.post(
            url_for('api.v1.add_group_currency'),
            data=json.dumps({
                'name': 'Subgroup_currency 1',
                'symbol': 'UAH',
                'group': self.group.id + 100
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_create_new_group_currency_wrong_token(self):
        response = self.client.post(
            url_for('api.v1.add_group_currency'),
            data=json.dumps({
                'name': 'Subgroup_currency 1',
                'symbol': 'UAH',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_new_group_currency(self):
        response = self.client.post(
            url_for('api.v1.add_group_currency'),
            data=json.dumps({
                'name': 'Smiths',
                'symbol': 'SEK',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')
        self.assertEqual(data['symbol'], 'SEK')

    def test_update_group_currency_wrong_symbol(self):
        response = self.client.put(
            url_for('api.v1.edit_group_currency', group_currency_id=self.group_currencies[1].id),
            data=json.dumps({
                'name': 'Transport',
                'symbol': 'AAA',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('symbol', data['errors'])
        self.assertIn('Symbol is not valid', data['errors']['symbol'])

    def test_update_group_currency_wrong_group(self):
        response = self.client.put(
            url_for('api.v1.edit_group_currency', group_currency_id=self.group_currencies[1].id),
            data=json.dumps({
                'name': 'Transport',
                'symbol': 'EUR',
                'group': self.group.id + 100
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('group', data['errors'])
        self.assertIn('Group with this id does not exist', data['errors']['group'])

    def test_update_group_currency_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.edit_group_currency', group_currency_id=self.group_currencies[1].id),
            data=json.dumps({
                'name': 'Transport',
                'symbol': 'EUR',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_group_currency(self):
        response = self.client.put(
            url_for('api.v1.edit_group_currency', group_currency_id=self.group_currencies[1].id),
            data=json.dumps({
                'name': 'Groceries',
                'symbol': 'USD',
                'group': self.group.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Groceries')
        self.assertEqual(data['symbol'], 'USD')

    def test_delete_group_currency_wrong_token(self):
        url = url_for('api.v1.delete_group_currency', group_currency_id=self.group_currencies[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_group_currency(self):
        url = url_for('api.v1.delete_group_currency', group_currency_id=self.group_currencies[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_group_currency_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_group_currencies'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_group_currency(self):
        response = self.client.get(
            url_for('api.v1.get_group_currencies'),
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
        self.assertEqual(data['name'], self.group_currencies[0].name)

    def test_get_group_currencies_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_group_currencies'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_group_currencies(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_group_currencies'),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.group_currencies))
        self.assertEqual(data['meta']['pages'], len(self.group_currencies) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_currencies_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_group_currencies', per_page=per_page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.group_currencies))
        self.assertEqual(data['meta']['pages'], len(self.group_currencies) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_currencies_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_group_currencies', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.group_currencies))
        self.assertEqual(data['meta']['pages'], len(self.group_currencies) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_group_currencies_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_group_currencies', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_group_currencies', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_group_currencies', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_group_currencies_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for(
                'api.v1.get_group_currencies', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.group_currencies[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for(
                'api.v1.get_group_currencies', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.group_currencies[-5:]], reverse=True)
        )
