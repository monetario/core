from datetime import datetime

from flask import current_app

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db


record_tag_table = db.Table(
    'record_tag',
    db.Model.metadata,
    db.Column('record_id', db.Integer, db.ForeignKey('record.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class CurrencyRate(db.Model):
    __tablename__ = 'currency_rate'

    id = db.Column(db.Integer, primary_key=True)
    base_currency = db.Column(db.Unicode(3), index=True)
    currency = db.Column(db.Unicode(3), index=True)
    rate = db.Column(db.Numeric(13, 4))
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(256), index=True)


class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    first_name = db.Column(db.String(256), index=True)
    last_name = db.Column(db.String(256), index=True)
    password_hash = db.Column(db.String(128), nullable=False)

    active = db.Column(db.Boolean, default=False, nullable=False)
    super_user = db.Column(db.Boolean, default=False, nullable=False)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    group = db.relationship(Group, backref='users')

    last_login = db.Column(db.DateTime, default=datetime.now)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_modified = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except Exception:
            return None

        return User.query.get(data['id'])

    def __repr__(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return self.email


class Category(db.Model):
    __tablename__ = 'category'

    (
        CATEGORY_TYPE_INCOME,
        CATEGORY_TYPE_OUTCOME,
    ) = range(2)

    CATEGORY_TYPES = [(CATEGORY_TYPE_INCOME, 'Income'), (CATEGORY_TYPE_OUTCOME, 'Outcome')]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    category_type = db.Column(db.Integer, default=CATEGORY_TYPE_OUTCOME)  # income or outcome
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), index=True)
    logo = db.Column(db.String(255), index=True)

    def __repr__(self):
        return self.name


class GroupCurrency(db.Model):
    __tablename__ = 'group_currency'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    symbol = db.Column(db.String(255), index=True)
    rate = db.Column(db.Integer)
    date_modified = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, index=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    group = db.relationship(Group, backref='currencies')

    def __repr__(self):
        return self.symbol


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)

    currency_id = db.Column(db.Integer, db.ForeignKey('group_currency.id'), index=True)
    currency = db.relationship(GroupCurrency, backref='records')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='accounts')

    def __repr__(self):
        return self.name


class GroupCategory(db.Model):
    __tablename__ = 'group_category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    category_type = db.Column(db.Integer)  # income or outcome
    parent_id = db.Column(db.Integer, db.ForeignKey('group_category.id'), index=True)
    logo = db.Column(db.String(255), index=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    group = db.relationship(Group, backref='categories')

    def __repr__(self):
        return self.name


class Record(db.Model):
    __tablename__ = 'record'

    (
        CATEGORY_TYPE_INCOME,
        CATEGORY_TYPE_OUTCOME,
    ) = range(2)

    CATEGORY_TYPES = [(CATEGORY_TYPE_INCOME, 'Income'), (CATEGORY_TYPE_OUTCOME, 'Outcome')]

    (
        PAYMENT_METHOD_CASH,
        PAYMENT_METHOD_DEBIT_CARD,
        PAYMENT_METHOD_CREDIT_CARD,
        PAYMENT_METHOD_BANK_TRANSACTION,
        PAYMENT_METHOD_MOBILE,
        PAYMENT_METHOD_INTERNET,
    ) = range(6)

    PAYMENT_METHODS = [
        (PAYMENT_METHOD_CASH, 'Cash'),
        (PAYMENT_METHOD_DEBIT_CARD, 'Debit card'),
        (PAYMENT_METHOD_CREDIT_CARD, 'Credit card'),
        (PAYMENT_METHOD_BANK_TRANSACTION, 'Bank transaction'),
        (PAYMENT_METHOD_MOBILE, 'Mobile payment'),
        (PAYMENT_METHOD_INTERNET, 'Internet payment'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(13, 4))
    description = db.Column(db.Text, index=True)
    record_type = db.Column(db.Integer, default=CATEGORY_TYPE_OUTCOME)  # income or outcome
    payment_method = db.Column(
        db.Integer, default=PAYMENT_METHOD_DEBIT_CARD
    )  # cash, debet card, mobile, internet payment
    date = db.Column(db.DateTime, default=datetime.now, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='records')
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), index=True)
    account = db.relationship(Account, backref='records')
    currency_id = db.Column(db.Integer, db.ForeignKey('group_currency.id'), index=True)
    currency = db.relationship(GroupCurrency, backref='records')
    category_id = db.Column(db.Integer, db.ForeignKey('group_category.id'), index=True)
    category = db.relationship(Category, backref='records')

    tags = db.relationship('Tag', secondary=record_tag_table, backref=db.backref('records'))

    def __repr__(self):
        return '{}_{}_{}'.format(self.account_id, self.record_type, self.amount)

