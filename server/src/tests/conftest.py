from dataclasses import dataclass
from typing import Optional, Sequence

import boto3
from mypy_boto3_dynamodb.type_defs import (
    AttributeDefinitionTypeDef,
    GlobalSecondaryIndexTypeDef,
    KeySchemaElementTypeDef,
)

from app.external.db import get_dynamodb_table


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


# S3
def setup_bucket(bucket_name: str) -> None:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)


def create_file(bucket_name: str, object_name: str) -> None:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket=bucket_name, Key=object_name, Body="test123")


def create_files(bucket_name: str, object_names: list[str]) -> None:
    for object_name in object_names:
        create_file(bucket_name, object_name)


# DynamoDB
def setup_db(table_name: str, table_schema: TableSchema) -> None:
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=table_schema.key_schema,
        AttributeDefinitions=table_schema.attribute_definitions,
        GlobalSecondaryIndexes=table_schema.global_secondary_indexes,
        BillingMode="PAY_PER_REQUEST",
    )


def add_item(table_name: str, item) -> None:
    table = get_dynamodb_table(table_name)
    table.put_item(Item=item)


def get_item(table_name: str, keys) -> Optional[dict]:
    table = get_dynamodb_table(table_name)
    response = table.get_item(Key=keys)

    if "Item" not in response:
        return None

    return response["Item"]
