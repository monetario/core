from datetime import datetime

from flask import current_app
from flask import url_for

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db
from monetario.serializers import AppSchema
from monetario.serializers import TokenSchema
from monetario.serializers import GroupSchema
from monetario.serializers import UserSchema
from monetario.serializers import CategorySchema
from monetario.serializers import GroupCategorySchema
from monetario.serializers import GroupCurrencySchema
from monetario.serializers import AccountSchema
from monetario.serializers import RecordSchema


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

    @property
    def resource_url(self):
        return url_for('api.v1.get_group', group_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = GroupSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = GroupSchema()
        result = schema.load(data, partial=partial)
        return result

    def __repr__(self):
        return self.name


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

    def get_id(self):
        return self.id

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
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        return User.query.get(data['id'])

    @property
    def resource_url(self):
        return url_for('api.v1.get_user', user_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = UserSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = UserSchema()
        result = schema.load(data, partial=partial)
        return result

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
    parent = db.relationship('Category', remote_side=[id])
    colour = db.Column(db.String(64), index=True)
    logo = db.Column(db.String(255), index=True)

    def __repr__(self):
        return self.name

    @property
    def resource_url(self):
        return url_for('api.v1.get_category', category_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = CategorySchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = CategorySchema()
        result = schema.load(data, partial=partial)
        return result


class GroupCategory(db.Model):
    __tablename__ = 'group_category'

    CATEGORY_TYPE_INCOME = Category.CATEGORY_TYPE_INCOME
    CATEGORY_TYPE_OUTCOME = Category.CATEGORY_TYPE_OUTCOME
    CATEGORY_TYPES = Category.CATEGORY_TYPES

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    category_type = db.Column(db.Integer)  # income or outcome
    parent_id = db.Column(db.Integer, db.ForeignKey('group_category.id'), index=True)
    parent = db.relationship('GroupCategory', remote_side=[id])

    colour = db.Column(db.String(64), index=True)
    logo = db.Column(db.String(255), index=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    group = db.relationship(Group, backref='categories')

    def __repr__(self):
        return self.name

    @property
    def resource_url(self):
        return url_for('api.v1.get_group_category', group_category_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = GroupCategorySchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = GroupCategorySchema()
        result = schema.load(data, partial=partial)
        return result


class GroupCurrency(db.Model):
    __tablename__ = 'group_currency'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    symbol = db.Column(db.String(3), index=True)
    rate = db.Column(db.Integer)
    # rate = db.Column(db.Numeric(13, 4))
    date_modified = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, index=True)

    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), index=True)
    group = db.relationship(Group, backref='currencies')

    def __repr__(self):
        return self.symbol

    @property
    def resource_url(self):
        return url_for('api.v1.get_group_currency', group_currency_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = GroupCurrencySchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = GroupCurrencySchema()
        result = schema.load(data, partial=partial)
        return result


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)

    currency_id = db.Column(db.Integer, db.ForeignKey('group_currency.id'), index=True)
    currency = db.relationship(GroupCurrency, backref='accounts')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='accounts')

    def __repr__(self):
        return self.name

    @property
    def resource_url(self):
        return url_for('api.v1.get_account', account_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = AccountSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = AccountSchema()
        result = schema.load(data, partial=partial)
        return result


class Record(db.Model):
    __tablename__ = 'record'

    (
        RECORD_TYPE_INCOME,
        RECORD_TYPE_EXPENSE,
    ) = range(2)

    RECORD_TYPES = [
        (RECORD_TYPE_INCOME, 'Income'),
        (RECORD_TYPE_EXPENSE, 'Expense'),
    ]

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
    record_type = db.Column(db.Integer, default=RECORD_TYPE_EXPENSE)
    payment_method = db.Column(
        db.Integer, default=PAYMENT_METHOD_DEBIT_CARD
    )  # cash, debet card, mobile, internet payment
    date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow(), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='records')

    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), index=True)
    account = db.relationship(Account, backref='records')

    currency_id = db.Column(db.Integer, db.ForeignKey('group_currency.id'), index=True)
    currency = db.relationship(GroupCurrency, backref='records')

    category_id = db.Column(db.Integer, db.ForeignKey('group_category.id'), index=True)
    category = db.relationship(GroupCategory, backref='records')

    tags = db.relationship('Tag', secondary=record_tag_table, backref=db.backref('records'))

    def __repr__(self):
        return '{}_{}_{}'.format(self.account_id, self.record_type, self.amount)

    @property
    def resource_url(self):
        return url_for('api.v1.get_record', record_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = RecordSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = RecordSchema()
        result = schema.load(data, partial=partial)
        return result


class App(db.Model):
    __tablename__ = 'app'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True)
    secret = db.Column(db.String(255), index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='apps')

    def __repr__(self):
        return self.name

    def generate_auth_token(self, expires_in=157680000):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        return App.query.get(data['id'])

    @property
    def resource_url(self):
        return url_for('api.v1.get_app', app_id=self.id, _external=True)

    def to_json(self, exclude=None):
        schema = AppSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = AppSchema()
        result = schema.load(data, partial=partial)
        return result


class Token(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True)

    app_id = db.Column(db.Integer, db.ForeignKey('app.id'), index=True)
    app = db.relationship(App, backref='tokens')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    user = db.relationship(User, backref='tokens')

    token = db.Column(db.String(255), index=True)

    def generate_auth_token(self, expires_in=900):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    def is_token_valid(self):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(self.token)
        except SignatureExpired:
            return False
        except BadSignature:
            return False

        return self.id == data['id']

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        return Token.query.get(data['id'])

    def to_json(self, exclude=None):
        schema = TokenSchema()
        result = schema.dump(self)
        return result

    @staticmethod
    def from_json(data, partial=False):
        schema = TokenSchema()
        result = schema.load(data, partial=partial)
        return result

    def __repr__(self):
        return '<Token app_id="{}" user_id="{}" />'.format(self.app_id, self.user_id)
