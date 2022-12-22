from typing import Optional
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key

from app import settings
from app.domain.entity import User
from app.domain.exceptions import UserAlreadyExistsError


def get_dynamodb_table(table_name: str):
    dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
    return dynamodb.Table(table_name)


def create_user(table_name: str, user: User) -> None:
    existing_user = get_user_by_email(table_name, user.email)

    if existing_user:
        raise UserAlreadyExistsError()

    table = get_dynamodb_table(table_name)
    table.put_item(Item=user.to_db())


def get_user_by_identifier(table_name: str, identifier: str) -> Optional[User]:
    table = get_dynamodb_table(table_name)
    response = table.get_item(
        Key={
            "entityIdentifier": identifier,
            "dataType": "METADATA",
        }
    )

    if "Item" not in response:
        return None

    return User.from_db(response["Item"])


def get_user_by_email(table_name: str, email: str) -> Optional[User]:
    table = get_dynamodb_table(table_name)
    response = table.query(
        IndexName="emailIndex",
        KeyConditionExpression=Key("email").eq(email),
    )

    if not response["Items"]:
        return None

    return User.from_db(response["Items"][0])


def check_if_user_token_is_valid(table_name: str, token: UUID) -> bool:
    identifier = User.from_token_to_identifier(token)
    user = get_user_by_identifier(table_name, identifier)

    return user is not None and user.isActive
