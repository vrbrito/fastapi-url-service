import uuid
from unittest import mock

from fastapi.testclient import TestClient
from moto import mock_s3

from app import settings
from app.main import app
from tests.conftest import create_file, create_files, setup_bucket

client = TestClient(app)


def test_list_files_requires_auth():
    response = client.get(
        "/files/",
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing credentials"}


@mock_s3
@mock.patch("app.external.db.check_if_user_token_is_valid", mock.MagicMock(return_value=True))
def test_list_files():
    bucket_name = settings.AWS_BUCKET_NAME
    object_names = [
        "test.txt",
        "a/test.txt",
        "b/c/test.txt",
    ]

    setup_bucket(bucket_name)
    create_files(bucket_name, object_names)

    response = client.get(
        "/files/",
        headers={
            "access_token": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 200
    assert list(response.json().keys()) == ["files"]
    assert set(response.json()["files"]) == set(object_names)


@mock_s3
@mock.patch("app.external.db.check_if_user_token_is_valid", mock.MagicMock(return_value=True))
def test_list_files_empty_bucket():
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)

    response = client.get(
        "/files/",
        headers={
            "access_token": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 200
    assert response.json() == {"files": []}


@mock_s3
@mock.patch("app.external.db.check_if_user_token_is_valid", mock.MagicMock(return_value=True))
@mock.patch("app.external.db.increment_usage")
def test_obtain_pre_signed_url(increment_usage_mock):
    bucket_name = settings.AWS_BUCKET_NAME
    table_name = settings.AWS_DYNAMODB_TABLE_NAME
    object_name = "b/c/test.txt"

    token = uuid.uuid4()

    setup_bucket(bucket_name)
    create_file(bucket_name, object_name)

    response = client.post(
        "/files/",
        json={"path": object_name},
        headers={
            "access_token": str(token),
        },
    )

    assert response.status_code == 200
    assert response.json()["signed_url"] is not None

    increment_usage_mock.assert_called_once_with(table_name=table_name, token=token)

    expected_sub_strings = [
        f"https://{bucket_name}.s3.amazonaws.com/{object_name}?",
        "AWSAccessKeyId=",
        "&Signature=",
        "&Expires=",
    ]

    for sub_string in expected_sub_strings:
        assert sub_string in response.json()["signed_url"]


@mock_s3
@mock.patch("app.external.db.check_if_user_token_is_valid", mock.MagicMock(return_value=True))
@mock.patch("app.external.db.increment_usage")
def test_obtain_pre_signed_url_file_does_not_exist(increment_usage_mock):
    bucket_name = settings.AWS_BUCKET_NAME

    setup_bucket(bucket_name)

    response = client.post(
        "/files/",
        json={"path": "non-existent.txt"},
        headers={
            "access_token": str(uuid.uuid4()),
        },
    )

    increment_usage_mock.assert_not_called()

    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}
