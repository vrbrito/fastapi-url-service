import uuid
from dataclasses import dataclass
from typing import Sequence

import boto3
from moto import mock_dynamodb
from mypy_boto3_dynamodb.type_defs import AttributeDefinitionTypeDef, KeySchemaElementTypeDef

from app.external.db import check_if_user_token_is_valid, get_user


@dataclass
class TableSchema:
    key_schema: Sequence[KeySchemaElementTypeDef]
    attribute_definitions: Sequence[AttributeDefinitionTypeDef]


table_schema = TableSchema(
    key_schema=[
        {"AttributeName": "pk", "KeyType": "HASH"},
        {"AttributeName": "sk", "KeyType": "RANGE"},
    ],
    attribute_definitions=[
        {"AttributeName": "pk", "AttributeType": "S"},
        {"AttributeName": "sk", "AttributeType": "S"},
    ],
)


def user_factory():
    user_uid = uuid.uuid4()
    return {
        "pk": f"USER#{user_uid}",
        "sk": "METADATA",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@gmail.com",
        "isActive": True,
        "isAdmin": False,
    }


def setup_db(table_name: str, table_schema: TableSchema) -> None:
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=table_schema.key_schema,
        AttributeDefinitions=table_schema.attribute_definitions,
        ProvisionedThroughput={
            "ReadCapacityUnits": 1,
            "WriteCapacityUnits": 1,
        },
    )


def add_entry(table_name: str, item) -> None:
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)


@mock_dynamodb
def test_get_user():
    table_name = "url-service-dev"
    user = user_factory()

    setup_db(table_name, table_schema)
    add_entry(table_name, user)

    assert get_user(table_name, user["pk"]) == user
    assert get_user(table_name, "non-existent") is None


@mock_dynamodb
def test_check_if_user_token_is_valid():
    table_name = "url-service-dev"

    active_user = user_factory()

    inactive_user = user_factory()
    inactive_user["isActive"] = False

    setup_db(table_name, table_schema)
    add_entry(table_name, active_user)
    add_entry(table_name, inactive_user)

    assert check_if_user_token_is_valid(table_name, active_user["pk"]) is True
    assert check_if_user_token_is_valid(table_name, inactive_user["pk"]) is False
    assert check_if_user_token_is_valid(table_name, "non-existent") is False
