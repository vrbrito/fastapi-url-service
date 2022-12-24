from typing import Optional

import boto3
import botocore

from app import settings


def get_s3_client():
    return boto3.client("s3", region_name=settings.AWS_DEFAULT_REGION)


def list_files(bucket_name: str) -> list[str]:
    s3 = get_s3_client()
    response = s3.list_objects(Bucket=bucket_name)

    if "Contents" not in response:
        return []

    return [file["Key"] for file in response["Contents"] if "Key" in file]


def check_if_file_exists(bucket_name: str, object_name: str) -> bool:
    s3 = get_s3_client()

    try:
        s3.head_object(Bucket=bucket_name, Key=object_name)
    except botocore.exceptions.ClientError as error:  # type: ignore
        if error.response["Error"]["Code"] == "404":
            return False

        raise error

    return True


def get_pre_signed_url(bucket_name: str, object_name: str, expiration=3600) -> Optional[str]:
    s3 = get_s3_client()

    if not check_if_file_exists(bucket_name, object_name):
        return None

    return s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket_name,
            "Key": object_name,
        },
        ExpiresIn=expiration,
    )
