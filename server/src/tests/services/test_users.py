import uuid

from app.adapters.repository import InMemoryRepository
from app.services.users import create_user, increment_usage, is_valid_token
from tests.domain.factories import UsageFactory, UserFactory


def test_create_user():
    user = UserFactory.create()

    repo = InMemoryRepository()

    create_user(user, repo)

    assert repo.users == [user]


def test_increment_usage():
    usage = UsageFactory.create(numPreSignedUrls=1)

    repo = InMemoryRepository(initial_usage=[usage])

    increment_usage(usage.token, repo)

    assert len(repo.usage) == 1
    assert repo.usage[0].numPreSignedUrls == 2


def test_is_valid_token():
    active_user = UserFactory.create(isActive=True)
    active_admin_user = UserFactory.create(isActive=True, isAdmin=True)
    inactive_user = UserFactory.create(isActive=False)

    repo = InMemoryRepository(initial_users=[active_user, active_admin_user, inactive_user])

    assert is_valid_token(active_user.token, False, repo) is True
    assert is_valid_token(active_user.token, True, repo) is False

    assert is_valid_token(active_admin_user.token, False, repo) is True
    assert is_valid_token(active_admin_user.token, True, repo) is True

    assert is_valid_token(inactive_user.token, False, repo) is False
    assert is_valid_token(inactive_user.token, True, repo) is False

    assert is_valid_token(uuid.uuid4(), False, repo) is False
    assert is_valid_token(uuid.uuid4(), True, repo) is False
