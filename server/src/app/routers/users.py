from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import APIKey
from pydantic import BaseModel

from app import settings
from app.auth import admin_auth
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


@router.post(
    "/",
    status_code=201,
    response_model=User,
    responses={400: {"description": "User already exists"}},
)
def create_user(
    payload: UserPayload,
    api_key: APIKey = Depends(admin_auth),
):
    user = User(**payload.dict())

    try:
        db.create_user(table_name=settings.AWS_DYNAMODB_TABLE_NAME, user=user)
    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=400, detail="User already exists") from error

    return user
