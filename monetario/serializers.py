import pycountry

from marshmallow import Schema, fields, ValidationError


def validate_currency_symbol(val):
    if val not in [x.letter for x in pycountry.currencies.objects]:
        raise ValidationError('Symbol is not valid')


class CategoryTypeField(fields.Field):
    def _serialize(self, value, attr, obj):
        return {'value': value, 'title': dict(obj.CATEGORY_TYPES).get(value)}


class RecordTypeField(fields.Field):
    def _serialize(self, value, attr, obj):
        return {'value': value, 'title': dict(obj.RECORD_TYPES).get(value)}


class PaymentMethodField(fields.Field):
    def _serialize(self, value, attr, obj):
        return {'value': value, 'title': dict(obj.PAYMENT_METHODS).get(value)}


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str()
    password = fields.Str(load_only=True, required=True)
    active = fields.Bool()

    group = fields.Nested(GroupSchema, dump_only=True)
    group_id = fields.Int(required=True, load_only=True, load_from='group')

    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    category_type = CategoryTypeField()

    parent = fields.Nested('self', dump_only=True, exclude=('parent', ))
    parent_id = fields.Int(load_only=True, load_from='parent')


class GroupCategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category_type = CategoryTypeField()

    group = fields.Nested(GroupSchema, dump_only=True)
    group_id = fields.Int(required=True, load_only=True, load_from='group')

    parent = fields.Nested('self', dump_only=True, exclude=('parent', ))
    parent_id = fields.Int(load_only=True, load_from='parent')


class GroupCurrencySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    symbol = fields.Str(
        required=True,
        validate=validate_currency_symbol
    )
    date_modified = fields.DateTime()

    group = fields.Nested(GroupSchema, dump_only=True)
    group_id = fields.Int(required=True, load_only=True, load_from='group')


class AccountSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    currency = fields.Nested(GroupCurrencySchema, dump_only=True)
    currency_id = fields.Int(required=True, load_only=True, load_from='currency')

    user = fields.Nested(UserSchema, dump_only=True)
    user_id = fields.Int(required=True, load_only=True, load_from='user')


class RecordSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    description = fields.Str()
    record_type = RecordTypeField()
    payment_method = PaymentMethodField()
    date = fields.Date()

    user = fields.Nested(UserSchema, dump_only=True)
    user_id = fields.Int(required=True, load_only=True, load_from='user')

    account = fields.Nested(AccountSchema, dump_only=True)
    account_id = fields.Int(required=True, load_only=True, load_from='account')

    currency = fields.Nested(GroupCurrencySchema, dump_only=True)
    currency_id = fields.Int(required=True, load_only=True, load_from='currency')

    category = fields.Nested(GroupCategorySchema, dump_only=True)
    category_id = fields.Int(required=True, load_only=True, load_from='category')


class AppSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    secret = fields.Str(required=True, dump_only=True)

    user = fields.Nested(UserSchema, dump_only=True)
    user_id = fields.Int(required=True, load_only=True, load_from='user')


class TokenSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    secret = fields.Str(required=True)
