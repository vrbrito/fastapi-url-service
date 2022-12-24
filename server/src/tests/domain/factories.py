import uuid
from random import randint

import factory

from app.domain.entity import Usage, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    firstName = factory.Faker("first_name")
    lastName = factory.Faker("last_name")
    email = factory.Faker("safe_email")

    @classmethod
    def create(cls, **kwargs) -> User:
        return super().create(**kwargs)


class UsageFactory(factory.Factory):
    class Meta:
        model = Usage

    token = factory.LazyFunction(uuid.uuid4)
    numPreSignedUrls = factory.LazyFunction(lambda: randint(1, 10))

    @classmethod
    def create(cls, **kwargs) -> Usage:
        return super().create(**kwargs)
