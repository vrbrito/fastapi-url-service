from decimal import Decimal

import pytest
from moto import mock_dynamodb

from app import settings
from app.adapters.repository import DynamoDBRepository, InMemoryRepository
from app.domain.exceptions import UserAlreadyExistsError
from tests.conftest import add_item, get_item, setup_db, table_schema
from tests.domain.factories import UsageFactory, UserFactory


def test_in_memory_repository_create_user():
    user = UserFactory.create()

    repo = InMemoryRepository()

    repo.create_user(user)

    assert repo.users == [user]


def test_in_memory_repository_create_user_already_exists():
    user = UserFactory.create()

    repo = InMemoryRepository()

    repo.create_user(user)

    with pytest.raises(UserAlreadyExistsError):
        repo.create_user(user)

    assert repo.users == [user]


@pytest.mark.parametrize("num_usages", [1, 3, 5])
def test_in_memory_repository_increment_usage(num_usages):
    user = UserFactory.create()

    repo = InMemoryRepository()

    for _ in range(num_usages):
        repo.increment_usage(user.token)

    assert len(repo.usage) == 1
    assert repo.usage[0].to_db() == {
        "dataType": "USAGE",
        "entityIdentifier": user.entity_identifier,
        "numPreSignedUrls": Decimal(num_usages),
    }


def test_in_memory_repository_get_user_by_email():
    user = UserFactory.create(email="existing@gmail.com")

    repo = InMemoryRepository(initial_users=[user])

    assert repo.get_user_by_email("existing@gmail.com") == user
    assert repo.get_user_by_email("non.existing@gmail.com") is None


def test_in_memory_repository_get_user_by_identifier():
    user = UserFactory.create()

    repo = InMemoryRepository(initial_users=[user])

    assert repo.get_user_by_identifier(user.entity_identifier) == user
    assert repo.get_user_by_identifier("non.existing") is None


def test_in_memory_repository_get_usage_by_identifier():
    usage = UsageFactory.create()

    repo = InMemoryRepository(initial_usage=[usage])

    assert repo.get_usage_by_identifier(usage.entity_identifier) == usage
    assert repo.get_usage_by_identifier("non.existing") is None


@mock_dynamodb
def test_dynamo_db_repository_create_user():
    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)

    user = UserFactory.create()
    repo = DynamoDBRepository()

    repo.create_user(user)

    response = get_item(
        table_name,
        {
            "entityIdentifier": user.entity_identifier,
            "dataType": "METADATA",
        },
    )

    assert response == user.to_db()


@mock_dynamodb
def test_dynamo_db_repository_create_user_already_exists():
    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)

    user = UserFactory.create()
    repo = DynamoDBRepository()

    repo.create_user(user)

    with pytest.raises(UserAlreadyExistsError):
        repo.create_user(user)

    response = get_item(
        table_name,
        {
            "entityIdentifier": user.entity_identifier,
            "dataType": "METADATA",
        },
    )

    assert response == user.to_db()


@mock_dynamodb
@pytest.mark.parametrize("num_usages", [1, 3, 5])
def test_dynamo_db_repository_increment_usage(num_usages):
    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)

    user = UserFactory.create()
    repo = DynamoDBRepository()

    for _ in range(num_usages):
        repo.increment_usage(user.token)

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
def test_dynamo_db_repository_get_user_by_email():
    user = UserFactory.create(email="existing@gmail.com")

    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    repo = DynamoDBRepository()

    assert repo.get_user_by_email("existing@gmail.com") == user
    assert repo.get_user_by_email("non.existing@gmail.com") is None


@mock_dynamodb
def test_dynamo_db_repository_get_user_by_identifier():
    user = UserFactory.create()

    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    repo = DynamoDBRepository()

    assert repo.get_user_by_identifier(user.entity_identifier) == user
    assert repo.get_user_by_identifier("non.existing") is None


@mock_dynamodb
def test_dynamo_db_repository_get_usage_by_identifier():
    usage = UsageFactory.create()

    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    setup_db(table_name, table_schema)
    add_item(table_name, usage.to_db())

    repo = DynamoDBRepository()

    assert repo.get_usage_by_identifier(usage.entity_identifier) == usage
    assert repo.get_usage_by_identifier("non.existing") is None
