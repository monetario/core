import json

from flask import url_for

from monetario.app import db

from monetario.views.api.v1.tests.fixtures import AccountFactory
from monetario.views.api.v1.tests.fixtures import GroupCurrencyFactory
from monetario.views.api.v1.tests.fixtures import GroupCategoryFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.views.api.v1.tests.fixtures import RecordFactory
from monetario.tests import BaseTestCase


class RecordsTest(BaseTestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        super().setUp()

        self.account = AccountFactory.create()
        db.session.add(self.account)

        self.category = GroupCategoryFactory.create()
        db.session.add(self.category)

        self.currency = GroupCurrencyFactory.create()
        db.session.add(self.currency)

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.records = sorted(RecordFactory.create_batch(30), key=lambda x: x.date)
        for record in self.records:
            db.session.add(record)

        db.session.commit()

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

    def test_create_new_record_missing_amount(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({}),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('amount', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['amount'])

    def test_create_new_record_wrong_currency(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id + 10,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_create_new_record_wrong_user(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id + 100
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_create_new_record_wrong_category(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id + 100,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('category', data['errors'])
        self.assertIn('GroupCategory with this id does not exist', data['errors']['category'])

    def test_create_new_record_wrong_account(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id + 100,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('account', data['errors'])
        self.assertIn('Account with this id does not exist', data['errors']['account'])

    def test_create_new_record_wrong_token(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_new_record(self):
        response = self.client.post(
            url_for('api.v1.add_record'),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('amount', data)
        self.assertEqual(data['amount'], 100)
        self.assertEqual(data['currency']['id'], self.currency.id)
        self.assertEqual(data['account']['id'], self.account.id)
        self.assertEqual(data['category']['id'], self.category.id)
        self.assertEqual(data['user']['id'], self.user.id)

    def test_update_record_wrong_currency(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id + 100,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_update_record_wrong_user(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id + 100
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('user', data['errors'])
        self.assertIn('User with this id does not exist', data['errors']['user'])

    def test_update_record_wrong_category(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id + 100,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('category', data['errors'])
        self.assertIn('GroupCategory with this id does not exist', data['errors']['category'])

    def test_update_record_wrong_account(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id + 100,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('account', data['errors'])
        self.assertIn('Account with this id does not exist', data['errors']['account'])

    def test_update_record_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 100,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_record(self):
        response = self.client.put(
            url_for('api.v1.edit_record', record_id=self.records[1].id),
            data=json.dumps({
                'amount': 99.5,
                'currency': self.currency.id,
                'account': self.account.id,
                'category': self.category.id,
                'user': self.user.id
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('amount', data)
        self.assertEqual(data['amount'], 99.5)
        self.assertEqual(data['currency']['id'], self.currency.id)

    def test_delete_record_wrong_token(self):
        url = url_for('api.v1.delete_record', record_id=self.records[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_record(self):
        url = url_for('api.v1.delete_record', record_id=self.records[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_record_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_records'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_record(self):
        response = self.client.get(
            url_for('api.v1.get_records'),
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
        self.assertEqual(data['date'], self.records[0].date.isoformat())

    def test_get_records_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_records'),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_records(self):
        per_page = 10
        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.records))
        self.assertEqual(data['meta']['pages'], len(self.records) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_records_five_per_page(self):
        per_page = 5
        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], 1)
        self.assertEqual(data['meta']['total'], len(self.records))
        self.assertEqual(data['meta']['pages'], len(self.records) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_records_pagination(self):
        per_page = 10
        page = 2

        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('meta', data)
        self.assertEqual(data['meta']['page'], page)
        self.assertEqual(data['meta']['total'], len(self.records))
        self.assertEqual(data['meta']['pages'], len(self.records) / per_page)
        self.assertEqual(data['meta']['per_page'], per_page)

        self.assertIn('objects', data)
        self.assertEqual(len(data['objects']), per_page)

    def test_get_records_wrong_page(self):
        per_page = 10
        page = 10

        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = -9

        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

        page = 0

        response = self.client.get(
            url_for('api.v1.get_records', per_page=per_page, page=page),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_records_sorting(self):
        per_page = 5
        page = 1
        sort = 'date,asc'

        response = self.client.get(
            url_for(
                'api.v1.get_records', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['date'] for x in data['objects']],
            [x.date.isoformat() for x in self.records[:5]]
        )

        sort = 'date,desc'
        response = self.client.get(
            url_for(
                'api.v1.get_records', per_page=per_page, page=page, sort=sort, expand=1
            ),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertSequenceEqual(
            [x['date'] for x in data['objects']],
            sorted([x.date.isoformat() for x in self.records[-5:]], reverse=True)
        )
