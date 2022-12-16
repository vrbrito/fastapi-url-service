from typing import Optional

import boto3
import botocore


def check_if_file_exists(bucket_name: str, object_name: str) -> bool:
    s3 = boto3.client("s3")

    try:
        s3.head_object(Bucket=bucket_name, Key=object_name)
    except botocore.exceptions.ClientError as error:  # type: ignore
        if error.response["Error"]["Code"] == "404":
            return False

        raise error

    return True


def get_pre_signed_url(bucket_name: str, object_name: str, expiration=3600) -> Optional[str]:
    s3 = boto3.client("s3")

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
