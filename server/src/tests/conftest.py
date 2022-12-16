import boto3


def setup_bucket(bucket_name: str) -> None:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)


def create_file(bucket_name: str, object_name: str) -> None:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket=bucket_name, Key=object_name, Body="test123")


def create_files(bucket_name: str, object_names: list[str]) -> None:
    for object_name in object_names:
        create_file(bucket_name, object_name)
