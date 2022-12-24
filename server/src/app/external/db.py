from typing import Optional
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key

from app import settings
from app.domain.entity import Usage, User
from app.domain.exceptions import UserAlreadyExistsError


def _get_dynamodb_table(table_name: str):
    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_DEFAULT_REGION)
    return dynamodb.Table(table_name)


def _get_item(table_name: str, keys: dict) -> Optional[dict]:
    table = _get_dynamodb_table(table_name)
    response = table.get_item(Key=keys)

    if "Item" not in response:
        return None

    return response["Item"]


def _put_item(table_name: str, item: dict):
    table = _get_dynamodb_table(table_name)
    table.put_item(Item=item)


def create_user(table_name: str, user: User) -> None:
    existing_user = get_user_by_email(table_name, user.email)

    if existing_user:
        raise UserAlreadyExistsError()

    _put_item(table_name, item=user.to_db())


def increment_usage(table_name: str, token: UUID) -> None:
    entity_identifier = User.from_token_to_identifier(token)

    table = _get_dynamodb_table(table_name)
    table.update_item(
        Key={
            "entityIdentifier": entity_identifier,
            "dataType": "USAGE",
        },
        ExpressionAttributeNames={
            "#numPreSignedUrls": "numPreSignedUrls",
        },
        ExpressionAttributeValues={
            ":increase": 1,
        },
        UpdateExpression="ADD #numPreSignedUrls :increase",
    )


def get_user_by_identifier(table_name: str, identifier: str) -> Optional[User]:
    item = _get_item(
        table_name=table_name,
        keys={
            "entityIdentifier": identifier,
            "dataType": "METADATA",
        },
    )

    if not item:
        return None

    return User.from_db(item)


def get_user_by_email(table_name: str, email: str) -> Optional[User]:
    table = _get_dynamodb_table(table_name)
    response = table.query(
        IndexName="emailIndex",
        KeyConditionExpression=Key("email").eq(email),
    )

    if not response["Items"]:
        return None

    return User.from_db(response["Items"][0])


def get_usage_by_identifier(table_name: str, identifier: str) -> Optional[Usage]:
    item = _get_item(
        table_name=table_name,
        keys={
            "entityIdentifier": identifier,
            "dataType": "USAGE",
        },
    )

    if not item:
        return None

    return Usage.from_db(item)


def check_if_user_token_is_valid(table_name: str, token: UUID, requires_admin: bool = False) -> bool:
    identifier = User.from_token_to_identifier(token)
    user = get_user_by_identifier(table_name, identifier)

    if not requires_admin:
        return user is not None and user.isActive

    return user is not None and user.isActive and user.isAdmin
