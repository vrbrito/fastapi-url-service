import uuid
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class User:
    firstName: str
    lastName: str
    email: str
    isActive: bool = True
    isAdmin: bool = False
    token: UUID = field(default_factory=uuid4)
    createdOn: datetime = field(default_factory=datetime.now)

    @property
    def entity_identifier(self):
        return f"USER#{self.token}"

    @classmethod
    def from_db(cls, user_dict: dict) -> "User":
        # remove from payload
        user_dict.pop("dataType")

        # convert token and createdOn to proper format
        entity_identifier = user_dict.pop("entityIdentifier")
        creation = user_dict.pop("createdOn")

        token = uuid.UUID(entity_identifier.strip("USER#"))
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
