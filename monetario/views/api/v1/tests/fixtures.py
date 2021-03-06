import random
import datetime
from random import choice
from pytz import UTC


import factory
import pycountry
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyDecimal
from factory.fuzzy import FuzzyDateTime
from factory.fuzzy import FuzzyText

from monetario.app import db

from monetario.models import Group
from monetario.models import User
from monetario.models import Category
from monetario.models import GroupCategory
from monetario.models import GroupCurrency
from monetario.models import Account
from monetario.models import App
from monetario.models import Record
from monetario.models import Transaction


class GroupFactory(factory.Factory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: 'group_%s' % n)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: 'user_%s' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.first_name)
    password = '111'


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: 'category_%s' % n)


class GroupCategoryFactory(factory.Factory):
    class Meta:
        model = GroupCategory

    name = factory.Sequence(lambda n: 'category_%s' % n)


class GroupCurrencyFactory(factory.Factory):
    class Meta:
        model = GroupCurrency

    symbol = factory.Sequence(lambda n: choice(pycountry.currencies.objects).letter)
    name = factory.LazyAttribute(lambda obj: obj.symbol)


class AccountFactory(factory.Factory):
    class Meta:
        model = Account

    name = factory.Sequence(lambda n: 'account_%s' % n)


class RecordFactory(factory.Factory):
    class Meta:
        model = Record

    amount = FuzzyDecimal(10, 10000, 2)
    record_type = factory.LazyAttribute(lambda n: random.randint(0, len(Record.RECORD_TYPES) - 1))
    payment_method = factory.LazyAttribute(
        lambda n: random.randint(0, len(Record.PAYMENT_METHODS) - 1)
    )
    date = FuzzyDateTime(
        datetime.datetime(2008, 1, 1, 0, 0, tzinfo=UTC),
        datetime.datetime(2016, 1, 1, 0, 0, tzinfo=UTC)
    )


class TransactionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Transaction
        sqlalchemy_session = db.session

    amount = FuzzyDecimal(10, 10000, 2)


class AppFactory(factory.Factory):
    class Meta:
        model = App

    name = factory.Sequence(lambda n: 'account_%s' % n)
    secret = FuzzyText(length=64, chars='0123456789abcdef')