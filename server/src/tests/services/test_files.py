from moto import mock_s3

from app import settings
from app.adapters.storage import S3Storage
from app.services.files import get_pre_signed_url, list_files
from tests.conftest import create_file, setup_bucket


@mock_s3
def test_list_files():
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)
    create_file(bucket_name, "test.txt")
    create_file(bucket_name, "test2.txt")

    storage = S3Storage()

    files = list_files(storage)

    assert set(files) == {"test.txt", "test2.txt"}


@mock_s3
def test_list_files_empty_bucket():
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)

    storage = S3Storage()

    files = list_files(storage)

    assert files == []


@mock_s3
def test_get_pre_signed_url():
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)
    create_file(bucket_name, "test.txt")

    storage = S3Storage()

    url = get_pre_signed_url("test.txt", storage)

    assert url is not None

    expected_sub_strings = [
        f"https://{bucket_name}.s3.amazonaws.com/test.txt?",
        "AWSAccessKeyId=",
        "&Signature=",
        "&Expires=",
    ]

    for sub_string in expected_sub_strings:
        assert sub_string in url


@mock_s3
def test_get_pre_signed_url_file_does_not_exist():
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)
    create_file(bucket_name, "test2.txt")

    storage = S3Storage()

    url = get_pre_signed_url("test.txt", storage)

    assert url is None
