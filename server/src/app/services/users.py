from typing import Optional
from uuid import UUID

from app.adapters.repository import AbstractRepository
from app.domain.entity import Usage, User


def create_user(user: User, repo: AbstractRepository) -> None:
    repo.create_user(user)


def increment_usage(token: UUID, repo: AbstractRepository) -> None:
    repo.increment_usage(token)


def get_usage_by_identifier(identifier: str, repo: AbstractRepository) -> Optional[Usage]:
    return repo.get_usage_by_identifier(identifier)


def is_valid_token(token: UUID, requires_admin: bool, repo: AbstractRepository) -> bool:
    identifier = User.from_token_to_identifier(token)
    user = repo.get_user_by_identifier(identifier)

    if not requires_admin:
        return user is not None and user.isActive

    return user is not None and user.isActive and user.isAdmin
