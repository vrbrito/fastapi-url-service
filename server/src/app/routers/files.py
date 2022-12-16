from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/files",
    tags=["files"],
    responses={404: {"description": "Not found"}},
)


class Payload(BaseModel):
    path: str


@router.get("/")
def list_files() -> dict:
    return {}


@router.post("/")
def obtain_pre_signed_url(payload: Payload) -> dict:
    return {}
