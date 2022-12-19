import factory

from app.domain.entity import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    firstName = factory.Faker("first_name")
    lastName = factory.Faker("last_name")
    email = factory.Faker("safe_email")

    @classmethod
    def create(cls, **kwargs) -> User:
        return super().create(**kwargs)
