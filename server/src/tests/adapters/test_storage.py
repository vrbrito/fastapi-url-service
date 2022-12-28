from moto import mock_s3

from app.adapters.storage import check_if_file_exists, get_pre_signed_url, list_files
from tests.conftest import create_file, create_files, setup_bucket


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
