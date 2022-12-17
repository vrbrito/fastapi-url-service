from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import settings
from app.external import storage

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


@router.get("/", response_model=FileList)
def list_files():
    files = storage.list_files(bucket_name=settings.AWS_BUCKET_NAME)

    return {"files": files}


@router.post("/", response_model=SignedURL, responses={404: {"description": "File not found"}})
def obtain_pre_signed_url(payload: SignedURLPayload):
    pre_signed_url = storage.get_pre_signed_url(bucket_name=settings.AWS_BUCKET_NAME, object_name=payload.path)

    if not pre_signed_url:
        raise HTTPException(status_code=404, detail="File not found")

    return {"signed_url": pre_signed_url}
