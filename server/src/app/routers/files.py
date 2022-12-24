from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.openapi.models import APIKey
from pydantic import BaseModel

from app import settings
from app.auth import basic_auth
from app.external import db, storage

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
    files = storage.list_files(bucket_name=settings.AWS_BUCKET_NAME)

    return {"files": files}


@router.post("", response_model=SignedURL, responses={404: {"description": "File not found"}})
def obtain_pre_signed_url(
    payload: SignedURLPayload,
    api_key: APIKey = Depends(basic_auth),
):
    pre_signed_url = storage.get_pre_signed_url(bucket_name=settings.AWS_BUCKET_NAME, object_name=payload.path)

    if not pre_signed_url:
        raise HTTPException(status_code=404, detail="File not found")

    db.increment_usage(table_name=settings.AWS_DYNAMODB_TABLE_NAME, token=UUID(api_key))  # type: ignore
    return {"signed_url": pre_signed_url}
