from uuid import UUID


def is_valid_uuid(key: str):
    try:
        UUID(key)
    except (ValueError, TypeError):
        return False

    return True
