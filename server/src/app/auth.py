from uuid import UUID

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.adapters.repository import DynamoDBRepository
from app.services import users
from app.utils import is_valid_uuid

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def authentication_check(key: str, requires_admin: bool = False):
    if not key:
        raise HTTPException(status_code=403, detail="Missing credentials")

    if not is_valid_uuid(key):
        raise HTTPException(status_code=403, detail="Credentials need to be a valid UUID token")

    repo = DynamoDBRepository()
    if users.is_valid_token(UUID(key), requires_admin, repo):
        return key

    raise HTTPException(status_code=403, detail="Could not validate credentials")


async def basic_auth(key: str = Security(api_key_header)):
    return await authentication_check(key, requires_admin=False)


async def admin_auth(key: str = Security(api_key_header)):
    return await authentication_check(key, requires_admin=True)
