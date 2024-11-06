from typing import Optional, Tuple

from ..connect import base_config
from ..enums import UserRole
from ..models.user import User


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
        user, created = await User.objects.get_or_create(
            user_id=user_id,
            _defaults={
                'username': username,
                'role': role,
            },
        )

    return user, created


async def get_or_none(user_id: int) -> Optional[User]:
    """Get or none user

    Args:
        user_id (int): User Telegram ID

    Returns:
        Optional[User]: User
    """
    async with base_config.database:
        return await User.objects.get_or_none(user_id=user_id)
