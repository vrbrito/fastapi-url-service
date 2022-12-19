import uuid

import pytest
from moto import mock_dynamodb

from app.domain.entity import User
from app.domain.exceptions import UserAlreadyExistsError
from app.external.db import check_if_user_token_is_valid, create_user, get_user_by_email, get_user_by_identifier
from tests.conftest import add_item, get_item, setup_db, table_schema
from tests.domain.factories import UserFactory


@mock_dynamodb
def test_create_user():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)

    create_user(table_name, user)

    response = get_item(
        table_name,
        {"entityIdentifier": user.entity_identifier, "dataType": "METADATA"},
    )
    assert User.from_db(response) == user  # type: ignore


@mock_dynamodb
def test_create_user_user_already_exists():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    with pytest.raises(UserAlreadyExistsError):
        create_user(table_name, user)


@mock_dynamodb
def test_get_user_by_identifier():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    assert get_user_by_identifier(table_name, user.entity_identifier) == user
    assert get_user_by_identifier(table_name, "non-existent") is None


@mock_dynamodb
def test_get_user_by_email():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    assert get_user_by_email(table_name, user.email) == user
    assert get_user_by_email(table_name, "non-existent") is None


@mock_dynamodb
def test_check_if_user_token_is_valid():
    table_name = "url-service-dev"

    active_user = UserFactory.create(isActive=True)
    inactive_user = UserFactory.create(isActive=False)

    setup_db(table_name, table_schema)
    add_item(table_name, active_user.to_db())
    add_item(table_name, inactive_user.to_db())

    assert check_if_user_token_is_valid(table_name, active_user.token) is True
    assert check_if_user_token_is_valid(table_name, inactive_user.token) is False
    assert check_if_user_token_is_valid(table_name, uuid.uuid4()) is False
