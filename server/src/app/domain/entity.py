from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def current_time():
    return datetime.now()


class User(BaseModel):
    firstName: str
    lastName: str
    email: str
    isActive: bool = True
    isAdmin: bool = False
    token: UUID = Field(default_factory=uuid4)
    createdOn: datetime = Field(default_factory=current_time)

    @property
    def entity_identifier(self):
        return self.from_token_to_identifier(self.token)

    @classmethod
    def from_token_to_identifier(cls, token: UUID):
        return f"USER#{token}"

    @classmethod
    def from_db(cls, user_dict: dict) -> "User":
        # remove from payload
        user_dict.pop("dataType")

        # convert token and createdOn to proper format
        entity_identifier = user_dict.pop("entityIdentifier")
        creation = user_dict.pop("createdOn")

        token = UUID(entity_identifier.strip("USER#"))
        created_on = datetime.fromisoformat(creation)

        return cls(
            **user_dict,
            token=token,
            createdOn=created_on,
        )

    def to_db(self) -> dict:
        return {
            "entityIdentifier": self.entity_identifier,
            "dataType": "METADATA",
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "isActive": self.isActive,
            "isAdmin": self.isAdmin,
            "createdOn": self.createdOn.isoformat(),
        }


class Usage(BaseModel):
    numPreSignedUrls: int
    token: UUID

    @classmethod
    def from_db(cls, usage_dict: dict) -> "Usage":
        # remove from payload
        usage_dict.pop("dataType")

        # convert token to proper format
        entity_identifier = usage_dict.pop("entityIdentifier")

        token = UUID(entity_identifier.strip("USER#"))

        return cls(
            **usage_dict,
            token=token,
        )

    def to_db(self) -> dict:
        return {
            "entityIdentifier": User.from_token_to_identifier(self.token),
            "dataType": "USAGE",
            "numPreSignedUrls": self.numPreSignedUrls,
        }
