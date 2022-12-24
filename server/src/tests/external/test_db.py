import uuid
from decimal import Decimal

import pytest
from moto import mock_dynamodb

from app.domain.entity import Usage, User
from app.domain.exceptions import UserAlreadyExistsError
from app.external.db import (
    check_if_user_token_is_valid,
    create_user,
    get_usage_by_identifier,
    get_user_by_email,
    get_user_by_identifier,
    increment_usage,
)
from tests.conftest import add_item, get_item, setup_db, table_schema
from tests.domain.factories import UsageFactory, UserFactory


@mock_dynamodb
def test_create_user():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    create_user(table_name, user)

    response = get_item(
        table_name,
        {
            "entityIdentifier": user.entity_identifier,
            "dataType": "METADATA",
        },
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
@pytest.mark.parametrize("num_usages", [1, 3, 5])
def test_increment_usage(num_usages):
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    for _ in range(num_usages):
        increment_usage(table_name, user.token)

    response = get_item(
        table_name,
        {
            "entityIdentifier": user.entity_identifier,
            "dataType": "USAGE",
        },
    )

    assert response == {
        "dataType": "USAGE",
        "entityIdentifier": user.entity_identifier,
        "numPreSignedUrls": Decimal(num_usages),
    }


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
def test_get_usage_by_identifier():
    table_name = "url-service-dev"

    user = UserFactory.create()
    usage = UsageFactory.create(token=user.token)

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())
    add_item(table_name, usage.to_db())

    response = get_usage_by_identifier(table_name, user.entity_identifier)

    assert Usage.to_db(response) == {  # type: ignore
        "entityIdentifier": user.entity_identifier,
        "dataType": "USAGE",
        "numPreSignedUrls": usage.numPreSignedUrls,
    }


@mock_dynamodb
def test_get_usage_by_identifier_no_usage():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    assert get_usage_by_identifier(table_name, user.entity_identifier) is None


@mock_dynamodb
def test_check_if_user_token_is_valid():
    table_name = "url-service-dev"

    active_user = UserFactory.create(isActive=True)
    active_admin_user = UserFactory.create(isActive=True, isAdmin=True)
    inactive_user = UserFactory.create(isActive=False)

    setup_db(table_name, table_schema)
    add_item(table_name, active_user.to_db())
    add_item(table_name, active_admin_user.to_db())
    add_item(table_name, inactive_user.to_db())

    assert check_if_user_token_is_valid(table_name, active_user.token, False) is True
    assert check_if_user_token_is_valid(table_name, active_user.token, True) is False

    assert check_if_user_token_is_valid(table_name, active_admin_user.token, False) is True
    assert check_if_user_token_is_valid(table_name, active_admin_user.token, True) is True

    assert check_if_user_token_is_valid(table_name, inactive_user.token, False) is False
    assert check_if_user_token_is_valid(table_name, inactive_user.token, True) is False

    assert check_if_user_token_is_valid(table_name, uuid.uuid4(), False) is False
    assert check_if_user_token_is_valid(table_name, uuid.uuid4(), True) is False
