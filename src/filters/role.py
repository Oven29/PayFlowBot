from typing import Tuple
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.database.enums import UserRole
from src.database import db


class RoleFilter(BaseFilter):
    """Filter by role"""

    def __init__(self, *roles: Tuple[UserRole]) -> None:
        self.roles = roles

    async def __call__(self, event: TelegramObject) -> bool:
        user = await db.user.get(user_id=event.from_user.id)
        return user and isinstance(user.role, self.roles)


class OwnerFilter(RoleFilter):
    """Filter by owner"""

    def __init__(self) -> None:
        super().__init__(UserRole.OWNER)


class AdminFilter(RoleFilter):
    """Filter by admin"""

    def __init__(self) -> None:
        super().__init__(UserRole.ADMIN, UserRole.OWNER)


class OperatorFilter(RoleFilter):
    """Filter by operator"""

    def __init__(self) -> None:
        super().__init__(UserRole.OPERATOR)


class ProviderFilter(RoleFilter):
    """Filter by provider"""

    def __init__(self) -> None:
        super().__init__(UserRole.PROVIDER)
