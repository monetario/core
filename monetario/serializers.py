from marshmallow import Schema, fields


class CategoryType(fields.Field):
    def _serialize(self, value, attr, obj):
        return {'value': value, 'title': dict(obj.CATEGORY_TYPES).get(value)}


class GroupSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    group = fields.Nested(GroupSchema, dump_only=True)
    group_id = fields.Int(required=True, load_only=True, load_from='group')
    email = fields.Email(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str()
    password = fields.Str(load_only=True, required=True)
    active = fields.Bool()
    date_created = fields.DateTime(dump_only=True)
    date_modified = fields.DateTime(dump_only=True)


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

    category_type = CategoryType()

    parent = fields.Nested('self', dump_only=True, exclude=('parent', ))
    parent_id = fields.Int(load_only=True, load_from='parent')
