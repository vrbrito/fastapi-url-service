import uuid

from app.utils import is_valid_uuid


def test_is_valid_uuid():
    assert is_valid_uuid("invalid") is False
    assert is_valid_uuid(str(uuid.uuid4())) is True
