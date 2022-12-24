from app.domain.entity import Usage, User
from tests.domain.factories import UsageFactory, UserFactory


def test_user_entity_identifier_property():
    user = UserFactory.create()

    assert user.entity_identifier == f"USER#{user.token}"


def test_user_entity_from_db():
    user = UserFactory.create()

    user_dict = {
        "entityIdentifier": user.entity_identifier,
        "dataType": "METADATA",
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "isActive": user.isActive,
        "isAdmin": user.isAdmin,
        "createdOn": user.createdOn.isoformat(),
    }

    assert User.from_db(user_dict) == user


def test_user_entity_to_db():
    user = UserFactory.create()

    assert user.to_db() == {
        "entityIdentifier": user.entity_identifier,
        "dataType": "METADATA",
        "firstName": user.firstName,
        "lastName": user.lastName,
        "email": user.email,
        "isActive": user.isActive,
        "isAdmin": user.isAdmin,
        "createdOn": user.createdOn.isoformat(),
    }


def test_usage_entity_from_db():
    usage = UsageFactory.create()

    usage_dict = {
        "entityIdentifier": User.from_token_to_identifier(usage.token),
        "dataType": "USAGE",
        "numPreSignedUrls": usage.numPreSignedUrls,
    }

    assert Usage.from_db(usage_dict) == usage


def test_usage_entity_to_db():
    usage = UsageFactory.create()

    assert usage.to_db() == {
        "dataType": "USAGE",
        "entityIdentifier": User.from_token_to_identifier(usage.token),
        "numPreSignedUrls": usage.numPreSignedUrls,
    }
