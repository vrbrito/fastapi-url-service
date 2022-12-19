from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import settings
from app.domain.entity import User
from app.domain.exceptions import UserAlreadyExistsError
from app.external import db

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class UserPayload(BaseModel):
    firstName: str
    lastName: str
    email: str
    isActive: bool = True
    isAdmin: bool = False


@router.post("/", status_code=201, response_model=User, responses={400: {"description": "User already exists"}})
def create_user(payload: UserPayload):
    user = User(**payload.dict())

    try:
        db.create_user(table_name=settings.AWS_DYNAMODB_TABLE_NAME, user=user)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=400, detail="User already exists") from error

    return user
