from uuid import UUID

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app import settings
from app.external import db
from app.utils import is_valid_uuid

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def basic_auth(api_key_header: str = Security(api_key_header), requires_admin: bool = False):
    if not api_key_header:
        raise HTTPException(status_code=403, detail="Missing credentials")

    if not is_valid_uuid(api_key_header):
        raise HTTPException(status_code=403, detail="Credentials need to be a valid UUID token")

    if db.check_if_user_token_is_valid(settings.AWS_DYNAMODB_TABLE_NAME, UUID(api_key_header), requires_admin):
        return api_key_header

    raise HTTPException(status_code=403, detail="Could not validate credentials")


async def admin_auth(api_key_header: str = Security(api_key_header)):
    return await basic_auth(api_key_header, requires_admin=True)
