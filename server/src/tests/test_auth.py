import uuid
from unittest import mock

import pytest
from fastapi import HTTPException

from app.adapters.repository import DynamoDBRepository
from app.auth import admin_auth, basic_auth


@pytest.mark.asyncio
async def test_basic_auth_missing_credentials():
    with pytest.raises(HTTPException) as err:
        await basic_auth("")

    assert err.value.status_code == 403
    assert err.value.detail == "Missing credentials"


@pytest.mark.asyncio
async def test_basic_auth_not_valid_uuid():
    with pytest.raises(HTTPException) as err:
        await basic_auth("123")

    assert err.value.status_code == 403
    assert err.value.detail == "Credentials need to be a valid UUID token"


@pytest.mark.asyncio
async def test_basic_auth_not_valid_token_in_db():
    token = uuid.uuid4()

    with pytest.raises(HTTPException) as err:
        with mock.patch("app.services.users.is_valid_token", mock.MagicMock(return_value=False)) as mocked:
            await basic_auth(str(token))

        assert mocked.call_count == 1
        assert mocked.call_args[0][0] == token
        assert mocked.call_args[0][1] is False
        assert isinstance(mocked.call_args[0][2], DynamoDBRepository)

    assert err.value.status_code == 403
    assert err.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_basic_auth_valid_token_in_db():
    token = uuid.uuid4()

    with mock.patch("app.services.users.is_valid_token", mock.MagicMock(return_value=True)) as mocked:
        api_key = await basic_auth(str(token))

    assert mocked.call_count == 1
    assert mocked.call_args[0][0] == token
    assert mocked.call_args[0][1] is False
    assert isinstance(mocked.call_args[0][2], DynamoDBRepository)

    assert api_key == str(token)


@pytest.mark.asyncio
async def test_admin_auth_requires_admin():
    token = uuid.uuid4()

    with mock.patch("app.services.users.is_valid_token", mock.MagicMock(return_value=True)) as mocked:
        api_key = await admin_auth(str(token))

    assert mocked.call_count == 1
    assert mocked.call_args[0][0] == token
    assert mocked.call_args[0][1] is True
    assert isinstance(mocked.call_args[0][2], DynamoDBRepository)

    assert api_key == str(token)
