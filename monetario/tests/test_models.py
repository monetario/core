from sqlalchemy.exc import IntegrityError

from monetario.app import db
from monetario.models import User
from monetario.tests import BaseTestCase


class UserModelTestCase(BaseTestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            print(u.password)

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_emails_case(self):
        """ Test that emails are converted to lowercase on create/update"""
        mixed_case_email = 'MixedCasedEmail@example.com'
        u = User(email=mixed_case_email, password='cat')
        self.assertTrue(u.email, mixed_case_email.lower())
        db.session.add(u)
        db.session.commit()
        u.email = mixed_case_email.upper()
        db.session.commit()
        db.session.refresh(u)
        self.assertTrue(u.email, mixed_case_email.lower())

    def test_unable_to_create_duplicated_users(self):
        u1 = User(email='test_email@example.com', password='cat')
        db.session.add(u1)
        db.session.commit()
        u2 = User(email='test_email@example.com', password='cat')
        db.session.add(u2)
        with self.assertRaises(IntegrityError):
            db.session.commit()
