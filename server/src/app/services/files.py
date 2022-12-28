from typing import Optional

from app.adapters.storage import S3Storage


def list_files(storage: S3Storage) -> list[str]:
    return storage.list_files()


def get_pre_signed_url(object_name: str, storage: S3Storage) -> Optional[str]:
    return storage.get_pre_signed_url(object_name)
