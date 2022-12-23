import pytest
from fastapi.testclient import TestClient
from moto import mock_dynamodb

from app import settings
from app.main import app
from tests.conftest import add_item, setup_db, table_schema
from tests.domain.factories import UserFactory

client = TestClient(app)


@mock_dynamodb
@pytest.mark.freeze_time("2022-12-19 00:00:00")
def test_create_user_requires_auth():
    response = client.post(
        "/users/",
        json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing credentials"}


@mock_dynamodb
@pytest.mark.freeze_time("2022-12-19 00:00:00")
def test_create_user_requires_admin_auth():
    table_name = settings.AWS_DYNAMODB_TABLE_NAME

    user = UserFactory.create()

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    response = client.post(
        "/users/",
        headers={
            "access_token": str(user.token),
        },
        json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


@mock_dynamodb
@pytest.mark.freeze_time("2022-12-19 00:00:00")
def test_create_user():
    table_name = settings.AWS_DYNAMODB_TABLE_NAME

    user = UserFactory.create(isAdmin=True)

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    response = client.post(
        "/users/",
        headers={
            "access_token": str(user.token),
        },
        json={
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
        },
    )

    token = response.json()["token"]

    assert response.status_code == 201
    assert response.json() == {
        "createdOn": "2022-12-19T00:00:00",
        "email": "john.doe@example.com",
        "firstName": "John",
        "isActive": True,
        "isAdmin": False,
        "lastName": "Doe",
        "token": token,
    }


@mock_dynamodb
def test_create_user_email_already_exists():
    table_name = settings.AWS_DYNAMODB_TABLE_NAME

    user = UserFactory.create(isAdmin=True)

    setup_db(table_name, table_schema)
    add_item(table_name, user.to_db())

    response = client.post(
        "/users/",
        headers={
            "access_token": str(user.token),
        },
        json={
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email": user.email,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}
