import boto3
from moto import mock_s3

from app.external.storage import check_if_file_exists, get_pre_signed_url, list_files


def setup_bucket(bucket_name: str) -> None:
    conn = boto3.resource("s3", region_name="us-east-1")
    conn.create_bucket(Bucket=bucket_name)


def create_file(bucket_name: str, object_name: str) -> None:
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket=bucket_name, Key=object_name, Body="test123")


def create_files(bucket_name: str, object_names: list[str]) -> None:
    for object_name in object_names:
        create_file(bucket_name, object_name)


@mock_s3
def test_list_files():
    bucket_name = "url-service-dev-files"
    object_names = [
        "test.txt",
        "a/test.txt",
        "b/c/test.txt",
    ]

    setup_bucket(bucket_name)
    create_files(bucket_name, object_names)

    assert set(list_files(bucket_name)) == set(object_names)


@mock_s3
def test_list_files_empty_bucket():
    bucket_name = "url-service-dev-files"

    setup_bucket(bucket_name)

    assert list_files(bucket_name) == []


@mock_s3
def test_check_if_file_exists():
    bucket_name = "url-service-dev-files"
    object_name = "test.txt"

    setup_bucket(bucket_name)
    create_file(bucket_name, object_name)

    assert check_if_file_exists(bucket_name, object_name) is True
    assert check_if_file_exists(bucket_name, "non-existent.txt") is False


@mock_s3
def test_get_pre_signed_url():
    bucket_name = "url-service-dev-files"
    object_name = "test.txt"

    setup_bucket(bucket_name)
    create_file(bucket_name, object_name)

    expected_sub_strings = [
        f"https://{bucket_name}.s3.amazonaws.com/{object_name}?",
        "AWSAccessKeyId=",
        "&Signature=",
        "&Expires=",
    ]

    pre_signed_url = get_pre_signed_url(bucket_name, object_name)

    assert pre_signed_url is not None

    for sub_string in expected_sub_strings:
        assert sub_string in pre_signed_url


@mock_s3
def test_get_pre_signed_url_file_does_not_exist():
    bucket_name = "url-service-dev-files"
    object_name = "test2.txt"

    setup_bucket(bucket_name)

    pre_signed_url = get_pre_signed_url(bucket_name, object_name)

    assert pre_signed_url is None
