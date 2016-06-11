import json

from flask import url_for

from monetario.app import db

from monetario.models import Record
from monetario.views.api.v1.tests.fixtures import AccountFactory
from monetario.views.api.v1.tests.fixtures import GroupCategoryFactory
from monetario.views.api.v1.tests.fixtures import GroupCurrencyFactory
from monetario.views.api.v1.tests.fixtures import UserFactory
from monetario.views.api.v1.tests.fixtures import TransactionFactory
from monetario.views.api.v1.tests.fixtures import RecordFactory
from monetario.tests import BaseTestCase


class TransactionsTest(BaseTestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def setUp(self):
        super().setUp()

        self.currency = GroupCurrencyFactory.create()
        db.session.add(self.currency)

        self.category = GroupCategoryFactory.create()
        db.session.add(self.category)

        self.user = UserFactory.create()
        db.session.add(self.user)

        self.user1 = UserFactory.create()
        db.session.add(self.user1)

        self.source_account1 = AccountFactory.create(user=self.user)
        db.session.add(self.source_account1)

        self.target_account1 = AccountFactory.create(user=self.user)
        db.session.add(self.target_account1)

        self.source_account2 = AccountFactory.create(user=self.user)
        db.session.add(self.source_account2)

        self.target_account2 = AccountFactory.create(user=self.user)
        db.session.add(self.target_account2)

        self.transactions = [
            TransactionFactory(
                source_account=self.source_account1,
                target_account=self.target_account1,
                user=self.user,
                currency=self.currency
            ),
            TransactionFactory.create(
                source_account=self.source_account2,
                target_account=self.target_account2,
                user=self.user,
                currency=self.currency
            ),
        ]

        db.session.commit()

        self.source_record1 = RecordFactory.create(
            record_type=Record.RECORD_TYPE_EXPENSE,
            transaction_id=self.transactions[0].id,
            account=self.source_account1,
            currency=self.currency,
            user=self.user
        )
        db.session.add(self.source_record1)

        self.target_record1 = RecordFactory.create(
            record_type=Record.RECORD_TYPE_INCOME,
            transaction_id=self.transactions[0].id,
            account=self.target_account1,
            currency=self.currency,
            user=self.user
        )
        db.session.add(self.target_record1)

        self.source_record2 = RecordFactory.create(
            record_type=Record.RECORD_TYPE_EXPENSE,
            transaction_id=self.transactions[1].id,
            account=self.source_account2,
            currency=self.currency,
            user=self.user
        )
        db.session.add(self.source_record2)

        self.target_record2 = RecordFactory.create(
            record_type=Record.RECORD_TYPE_INCOME,
            transaction_id=self.transactions[1].id,
            account=self.target_account2,
            currency=self.currency,
            user=self.user
        )
        db.session.add(self.target_record2)

        db.session.commit()

        self.api_app = self.create_api_app(self.user)
        self.token = self.get_token(self.api_app, self.user)

        self.api_app1 = self.create_api_app(self.user1)
        self.token1 = self.get_token(self.api_app1, self.user1)

    def test_create_new_transaction_missing_amount(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'source_account_id': self.source_account1.id + 100,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('amount', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['amount'])

    def test_create_new_transaction_missing_target_source_account(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('source_account', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['source_account'])

    def test_create_new_transaction_missing_target_account(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('target_account', data['errors'])
        self.assertIn('Missing data for required field.', data['errors']['target_account'])

    def test_create_new_transaction_wrong_currency(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id + 100,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_create_new_transaction_wrong_source_account(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id + 100,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('source_account', data['errors'])
        self.assertIn(
            'Source account with this id does not exist', data['errors']['source_account']
        )

    def test_create_new_transaction_wrong_target_account(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id + 100,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('target_account', data['errors'])
        self.assertIn(
            'Target account with this id does not exist', data['errors']['target_account']
        )

    def test_create_new_transaction_wrong_same_account(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.source_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('target_account', data['errors'])
        self.assertIn(
            'Source account and target account can not be equal', data['errors']['target_account']
        )

    def test_create_new_transaction_wrong_token(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_create_new_transaction(self):
        response = self.client.post(
            url_for('api.v1.add_transaction'),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 201)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('amount', data)
        self.assertEqual(data['amount'], 100)
        self.assertEqual(data['currency']['id'], self.currency.id)
        self.assertEqual(data['source_account']['id'], self.source_account1.id)
        self.assertEqual(data['target_account']['id'], self.target_account1.id)
        self.assertEqual(data['user']['id'], self.user.id)

        source_record = Record.query.filter(
            Record.record_type == Record.RECORD_TYPE_EXPENSE,
            Record.transaction_id == data['id']
        ).first()
        target_record = Record.query.filter(
            Record.record_type == Record.RECORD_TYPE_INCOME,
            Record.transaction_id == data['id']
        ).first()

        self.assertEqual(source_record.account_id, self.source_account1.id)
        self.assertEqual(source_record.currency_id, self.currency.id)
        self.assertEqual(source_record.amount, -100)
        self.assertEqual(source_record.user_id, self.user.id)

        self.assertEqual(target_record.account_id, self.target_account1.id)
        self.assertEqual(target_record.currency_id, self.currency.id)
        self.assertEqual(target_record.amount, 100)
        self.assertEqual(target_record.user_id, self.user.id)

    def test_update_transaction_wrong_token(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_update_transaction_wrong_user(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token1}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_transaction_wrong_currency(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id + 100,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('currency', data['errors'])
        self.assertIn('Group currency with this id does not exist', data['errors']['currency'])

    def test_update_transaction_wrong_source_account(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id + 100,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('source_account', data['errors'])
        self.assertIn(
            'Source account with this id does not exist', data['errors']['source_account']
        )

    def test_update_transaction_wrong_target_account(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id + 100,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('target_account', data['errors'])
        self.assertIn(
            'Target account with this id does not exist', data['errors']['target_account']
        )

    def test_update_transaction_wrong_same_account(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 100,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.source_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('errors', data)
        self.assertIn('target_account', data['errors'])
        self.assertIn(
            'Source account and target account can not be equal', data['errors']['target_account']
        )

    def test_update_transaction(self):
        response = self.client.put(
            url_for('api.v1.edit_transaction', transaction_id=self.transactions[1].id),
            data=json.dumps({
                'amount': 300,
                'source_account_id': self.source_account1.id,
                'target_account_id': self.target_account1.id,
                'currency_id': self.currency.id,
            }),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('amount', data)
        self.assertEqual(data['amount'], 300)
        self.assertEqual(data['currency']['id'], self.currency.id)
        self.assertEqual(data['source_account']['id'], self.source_account1.id)
        self.assertEqual(data['target_account']['id'], self.target_account1.id)
        self.assertEqual(data['user']['id'], self.user.id)

        source_record = Record.query.filter(
            Record.record_type == Record.RECORD_TYPE_EXPENSE,
            Record.transaction_id == self.transactions[1].id
        ).first()
        target_record = Record.query.filter(
            Record.record_type == Record.RECORD_TYPE_INCOME,
            Record.transaction_id == self.transactions[1].id
        ).first()

        self.assertEqual(source_record.account_id, self.source_account1.id)
        self.assertEqual(source_record.currency_id, self.currency.id)
        self.assertEqual(source_record.amount, -300)
        self.assertEqual(source_record.user_id, self.user.id)

        self.assertEqual(target_record.account_id, self.target_account1.id)
        self.assertEqual(target_record.currency_id, self.currency.id)
        self.assertEqual(target_record.amount, 300)
        self.assertEqual(target_record.user_id, self.user.id)

    def test_delete_transaction_wrong_token(self):
        url = url_for('api.v1.delete_transaction', transaction_id=self.transactions[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_transaction_wrong_user(self):
        url = url_for('api.v1.delete_transaction', transaction_id=self.transactions[0].id)
        response = self.client.delete(
            url,
            content_type='application/json',
            headers={'Authentication-Token': self.token1}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_transaction(self):
        url = url_for('api.v1.delete_transaction', transaction_id=self.transactions[0].id)
        response = self.client.delete(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 204)

        response = self.client.get(
            url, content_type='application/json', headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_transaction_wrong_token(self):
        response = self.client.get(
            url_for('api.v1.get_transaction', transaction_id=self.transactions[0].id),
            content_type='application/json',
            headers={'Authentication-Token': self.token + 'w'}
        )
        self.assertEqual(response.status_code, 401)

    def test_get_transaction_wrong_user(self):
        response = self.client.get(
            url_for('api.v1.get_transaction', transaction_id=self.transactions[0].id),
            content_type='application/json',
            headers={'Authentication-Token': self.token1}
        )
        self.assertEqual(response.status_code, 404)

    def test_get_transaction(self):
        response = self.client.get(
            url_for('api.v1.get_transaction', transaction_id=self.transactions[0].id),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('user', data)
        self.assertIn('source_account', data)
        self.assertIn('target_account', data)
        self.assertIn('amount', data)
        self.assertIn('currency', data)

        self.assertEqual(data['id'], self.transactions[0].id)
        self.assertEqual(data['amount'], float(self.transactions[0].amount))
        self.assertEqual(data['currency']['id'], self.transactions[0].currency.id)
        self.assertEqual(data['source_account']['id'], self.transactions[0].source_account.id)
        self.assertEqual(data['target_account']['id'], self.transactions[0].target_account.id)

    def test_get_transaction_record(self):
        response = self.client.get(
            url_for('api.v1.get_record', record_id=self.source_record1.id),
            content_type='application/json',
            headers={'Authentication-Token': self.token}
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        self.assertIn('transaction', data)
        self.assertIn('id', data['transaction'])
        self.assertIn('amount', data['transaction'])
        self.assertIn('currency', data['transaction'])
        self.assertIn('source_account', data['transaction'])
        self.assertIn('target_account', data['transaction'])

        self.assertEqual(data['transaction']['id'], self.source_record1.transaction_id)
        self.assertEqual(data['transaction']['amount'],
                         float(self.source_record1.transaction.amount))
        self.assertEqual(data['transaction']['currency']['id'], self.transactions[0].currency.id)
        self.assertEqual(data['transaction']['source_account']['id'],
                         self.source_record1.transaction.source_account_id)
        self.assertEqual(data['transaction']['target_account']['id'],
                         self.source_record1.transaction.target_account_id)
