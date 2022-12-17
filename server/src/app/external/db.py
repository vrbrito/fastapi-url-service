from typing import Optional

import boto3


class UserAlreadyExists(Exception):
    pass


def get_dynamodb_table(table_name: str):
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def get_user(table_name: str, token: str) -> Optional[dict]:
    table = get_dynamodb_table(table_name)
    response = table.get_item(
        Key={
            "pk": token,
            "sk": "METADATA",
        }
    )

    if "Item" not in response:
        return None

    return response["Item"]


def check_if_user_token_is_valid(table_name: str, token: str) -> bool:
    user = get_user(table_name, token)

    return bool(user) and user["isActive"]
