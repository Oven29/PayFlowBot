from typing import Optional, Tuple

from ..models.users import User
from ..connect import base_config
from ..enums import UserRole


async def get_or_create(
    user_id: int,
    role: UserRole,
    username: Optional[str] = None,
) -> Tuple[bool, User]:
    """Get or create user

    Args:
        user_id (int): User Telegram ID
        role (UserRole): User role
        username (Optional[str], optional): Username. Defaults to None.

    Returns:
        Tuple[bool, User]: Created, User
    """
    async with base_config.database:
        created, user = await User.objects.get_or_create(
            user_id=user_id,
            defaults={
                'username': username,
                'role': role.value,
            },
        )

    return created, user


async def get_or_none(user_id: int) -> Optional[User]:
    """Get or none user

    Args:
        user_id (int): User Telegram ID

    Returns:
        Optional[User]: User
    """
    async with base_config.database:
        return await User.objects.get_or_none(user_id=user_id)
