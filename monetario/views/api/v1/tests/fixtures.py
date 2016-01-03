import factory

from monetario.models import Group
from monetario.models import User
from monetario.models import Category


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
