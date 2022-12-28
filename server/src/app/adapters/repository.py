from abc import ABC, abstractclassmethod
from typing import List, Optional
from uuid import UUID

import boto3
from boto3.dynamodb.conditions import Key

from app import settings
from app.domain.entity import Usage, User
from app.domain.exceptions import UserAlreadyExistsError


class AbstractRepository(ABC):
    @abstractclassmethod
    def create_user(self, user: User) -> None:
        raise NotImplementedError

    @abstractclassmethod
    def increment_usage(self, token: UUID) -> None:
        raise NotImplementedError

    @abstractclassmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractclassmethod
    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        raise NotImplementedError

    @abstractclassmethod
    def get_usage_by_identifier(self, identifier: str) -> Optional[Usage]:
        raise NotImplementedError


class InMemoryRepository(AbstractRepository):
    def __init__(
        self,
        initial_users: Optional[List[User]] = None,
        initial_usage: Optional[List[Usage]] = None,
    ) -> None:
        if initial_users is None:
            initial_users = []

        if initial_usage is None:
            initial_usage = []

        self.users = initial_users
        self.usage = initial_usage

    def create_user(self, user: User) -> None:
        if self.get_user_by_email(email=user.email):
            raise UserAlreadyExistsError()

        self.users.append(user)

    def increment_usage(self, token: UUID) -> None:
        identifier = User.from_token_to_identifier(token)
        usage = self.get_usage_by_identifier(identifier)

        if not usage:
            self.usage.append(Usage(numPreSignedUrls=1, token=token))
            return

        new_usage = usage.copy()
        new_usage.numPreSignedUrls += 1

        position = self.usage.index(usage)
        self.usage[position] = new_usage

        return

    def get_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.users if user.email == email), None)

    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        return next((user for user in self.users if user.entity_identifier == identifier), None)

    def get_usage_by_identifier(self, identifier: str) -> Optional[Usage]:
        return next((usage for usage in self.usage if usage.entity_identifier == identifier), None)


class DynamoDBRepository(AbstractRepository):
    def __init__(self) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_DEFAULT_REGION)
        self.table = dynamodb.Table(settings.AWS_DYNAMODB_TABLE_NAME)

    def _get_item(self, keys: dict) -> Optional[dict]:
        response = self.table.get_item(Key=keys)

        if "Item" not in response:
            return None

        return response["Item"]

    def _put_item(self, item: dict):
        self.table.put_item(Item=item)

    def create_user(self, user: User) -> None:
        existing_user = self.get_user_by_email(user.email)

        if existing_user:
            raise UserAlreadyExistsError()

        self._put_item(item=user.to_db())

    def increment_usage(self, token: UUID) -> None:
        entity_identifier = User.from_token_to_identifier(token)

        self.table.update_item(
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

    def get_user_by_email(self, email: str) -> Optional[User]:
        response = self.table.query(
            IndexName="emailIndex",
            KeyConditionExpression=Key("email").eq(email),
        )

        if not response["Items"]:
            return None

        return User.from_db(response["Items"][0])

    def get_user_by_identifier(self, identifier: str) -> Optional[User]:
        item = self._get_item(
            keys={
                "entityIdentifier": identifier,
                "dataType": "METADATA",
            },
        )

        if not item:
            return None

        return User.from_db(item)

    def get_usage_by_identifier(self, identifier: str) -> Optional[Usage]:
        item = self._get_item(
            keys={
                "entityIdentifier": identifier,
                "dataType": "USAGE",
            },
        )

        if not item:
            return None

        return Usage.from_db(item)
