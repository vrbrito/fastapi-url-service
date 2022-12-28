from typing import Optional

import boto3
import botocore

from app import settings


class S3Storage:
    def __init__(self, bucket_name: Optional[str] = None) -> None:
        self.bucket_name = bucket_name or settings.AWS_BUCKET_NAME
        self.s3_client = boto3.client("s3", region_name=settings.AWS_DEFAULT_REGION)

    def list_files(self) -> list[str]:
        response = self.s3_client.list_objects(Bucket=self.bucket_name)

        if "Contents" not in response:
            return []

        return [file["Key"] for file in response["Contents"] if "Key" in file]

    def check_if_file_exists(self, object_name: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
        except botocore.exceptions.ClientError as error:  # type: ignore
            if error.response["Error"]["Code"] == "404":
                return False

            raise error

        return True

    def get_pre_signed_url(self, object_name: str, expiration=3600) -> Optional[str]:
        if not self.check_if_file_exists(object_name):
            return None

        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_name,
            },
            ExpiresIn=expiration,
        )
