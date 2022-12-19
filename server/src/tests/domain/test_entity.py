from app.domain.entity import User
from tests.domain.factories import UserFactory


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
