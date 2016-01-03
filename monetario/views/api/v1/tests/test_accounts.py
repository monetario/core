import json

from flask import url_for
from flask.ext.testing import TestCase

from monetario.app import create_app
from monetario.app import db

from monetario.views.api.v1.tests.fixtures import GroupCurrencyFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.views.api.v1.tests.fixtures import AccountFactory


class AccountsTest(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        db.create_all()
        self.currency = GroupCurrencyFactory.create()
        db.session.add(self.currency)

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.accounts = sorted(AccountFactory.create_batch(30), key=lambda x: x.name)
        for account in self.accounts:
            db.session.add(account)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def test_create_new_account_missing_name(self):
        response = self.client.post(
            url_for('api.v1.add_account'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('name', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['name'])

    def test_create_new_account_wrong_currency(self):
        response = self.client.post(
            url_for('api.v1.add_account'),
            data=json.dumps({
                'name': 'Subaccount 1',
                'currency': self.currency.id + 100,
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_create_new_account_wrong_user(self):
        response = self.client.post(
            url_for('api.v1.add_account'),
            data=json.dumps({
                'name': 'Subaccount 1',
                'currency': self.currency.id,
                'user': self.user.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_create_new_account(self):
        response = self.client.post(
            url_for('api.v1.add_account'),
            data=json.dumps({
                'name': 'Smiths',
                'currency': self.currency.id,
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Smiths')
        self.assertEqual(data['currency']['id'], self.currency.id)

    def test_update_account_wrong_currency(self):
        response = self.client.put(
            url_for('api.v1.edit_account', account_id=self.accounts[1].id),
            data=json.dumps({
                'name': 'Transport',
                'currency': self.currency.id + 100,
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_update_account_wrong_user(self):
        response = self.client.put(
            url_for('api.v1.edit_account', account_id=self.accounts[1].id),
            data=json.dumps({
                'name': 'Transport',
                'currency': self.currency.id,
                'user': self.user.id + 100
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_update_account(self):
        response = self.client.put(
            url_for('api.v1.edit_account', account_id=self.accounts[1].id),
            data=json.dumps({
                'name': 'Groceries',
                'currency': self.currency.id,
                'user': self.user.id
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('name', data)
        self.assertEqual(data['name'], 'Groceries')
        self.assertEqual(data['currency']['id'], self.currency.id)

    def test_delete_account(self):
        url = url_for('api.v1.delete_account', account_id=self.accounts[0].id)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_get_account(self):
        response = self.client.get(
            url_for('api.v1.get_accounts'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        url = data['objects'][0]

        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['name'], self.accounts[0].name)

    def test_get_accounts(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_accounts'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.accounts))
        self.assertEqual(data['meta']['pages'], len(self.accounts) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_accounts_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_accounts', per_page=per_page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.accounts))
        self.assertEqual(data['meta']['pages'], len(self.accounts) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_accounts_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_accounts', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.accounts))
        self.assertEqual(data['meta']['pages'], len(self.accounts) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_accounts_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_accounts', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_accounts', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_accounts', per_page=per_page, page=page),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_get_accounts_sorting(self):
        per_page = 5
        page = 1
        sort = 'name,asc'

        response = self.client.get(
            url_for(
                'api.v1.get_accounts', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            [x.name for x in self.accounts[:5]]
        )

        sort = 'name,desc'
        response = self.client.get(
            url_for(
                'api.v1.get_accounts', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['name'] for x in data['objects']],
            sorted([x.name for x in self.accounts[-5:]], reverse=True)
        )
