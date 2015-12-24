import factory

from monetario.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: 'user_%s' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.first_name)
    password = '111'
