from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import APIKey
from pydantic import BaseModel

from app.adapters.repository import DynamoDBRepository
from app.adapters.storage import S3Storage
from app.auth import basic_auth
from app.services import files, users

router = APIRouter(
    prefix="/files",
    tags=["files"],
)


class FileList(BaseModel):
    files: list[str]


class SignedURLPayload(BaseModel):
    path: str


class SignedURL(BaseModel):
    signed_url: str


@router.get("", response_model=FileList)
def list_files(
    api_key: APIKey = Depends(basic_auth),
):
    storage = S3Storage()

    files = storage.list_files()

    return {"files": files}


@router.post("", response_model=SignedURL, responses={404: {"description": "File not found"}})
def obtain_pre_signed_url(
    payload: SignedURLPayload,
    api_key: APIKey = Depends(basic_auth),
):
    repo = DynamoDBRepository()
    storage = S3Storage()

    pre_signed_url = files.get_pre_signed_url(object_name=payload.path, storage=storage)
    if not pre_signed_url:
        raise HTTPException(status_code=404, detail="File not found")

    users.increment_usage(token=UUID(api_key), repo=repo)  # type: ignore
    return {"signed_url": pre_signed_url}
