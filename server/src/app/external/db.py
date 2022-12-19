from typing import Optional

import boto3

from app.domain.entity import User


def get_dynamodb_table(table_name: str):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def get_user(table_name: str, token: str) -> Optional[User]:
    table = get_dynamodb_table(table_name)
    response = table.get_item(
        Key={
            "entityIdentifier": token,
            "dataType": "METADATA",
        }
    )

    if "Item" not in response:
        return None

    return User.from_db(response["Item"])


def check_if_user_token_is_valid(table_name: str, token: str) -> bool:
    user = get_user(table_name, token)

    return user is not None and user.isActive
