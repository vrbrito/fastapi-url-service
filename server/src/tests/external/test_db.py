from dataclasses import dataclass
from typing import Sequence

import boto3
from moto import mock_dynamodb
from mypy_boto3_dynamodb.type_defs import (
    AttributeDefinitionTypeDef,
    GlobalSecondaryIndexTypeDef,
    KeySchemaElementTypeDef,
)

from app.domain.entity import User
from app.external.db import check_if_user_token_is_valid, get_user
from tests.domain.factories import UserFactory


@dataclass
class TableSchema:
    key_schema: Sequence[KeySchemaElementTypeDef]
    attribute_definitions: Sequence[AttributeDefinitionTypeDef]
    global_secondary_indexes: Sequence[GlobalSecondaryIndexTypeDef]


table_schema = TableSchema(
    key_schema=[
        {"AttributeName": "entityIdentifier", "KeyType": "HASH"},
        {"AttributeName": "dataType", "KeyType": "RANGE"},
    ],
    attribute_definitions=[
        {"AttributeName": "entityIdentifier", "AttributeType": "S"},
        {"AttributeName": "dataType", "AttributeType": "S"},
        {"AttributeName": "email", "AttributeType": "S"},
        {"AttributeName": "createdOn", "AttributeType": "S"},
    ],
    global_secondary_indexes=[
        {
            "IndexName": "emailIndex",
            "KeySchema": [
                {"AttributeName": "email", "KeyType": "HASH"},
                {"AttributeName": "createdOn", "KeyType": "RANGE"},
            ],
            "Projection": {
                "ProjectionType": "ALL",
            },
        },
    ],
)


def setup_db(table_name: str, table_schema: TableSchema) -> None:
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=table_schema.key_schema,
        AttributeDefinitions=table_schema.attribute_definitions,
        GlobalSecondaryIndexes=table_schema.global_secondary_indexes,
        BillingMode="PAY_PER_REQUEST",
    )


def add_entry(table_name: str, user: User) -> None:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    item = user.to_db()

    table.put_item(Item=item)


@mock_dynamodb
def test_get_user():
    table_name = "url-service-dev"
    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_entry(table_name, user)

    assert get_user(table_name, user.entity_identifier) == user
    assert get_user(table_name, "non-existent") is None


@mock_dynamodb
def test_check_if_user_token_is_valid():
    table_name = "url-service-dev"

    active_user = UserFactory.create(isActive=True)
    inactive_user = UserFactory.create(isActive=False)

    setup_db(table_name, table_schema)
    add_entry(table_name, active_user)
    add_entry(table_name, inactive_user)

    assert check_if_user_token_is_valid(table_name, active_user.entity_identifier) is True
    assert check_if_user_token_is_valid(table_name, inactive_user.entity_identifier) is False
    assert check_if_user_token_is_valid(table_name, "non-existent") is False
