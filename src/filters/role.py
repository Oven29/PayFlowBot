from typing import Any, Dict, Tuple
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.database.enums import UserRole
from src.database import db


class RoleFilter(BaseFilter):
    """Filter by role"""

    def __init__(
        self,
        *roles: Tuple[UserRole],
        pass_user: bool = False
    ) -> None:
        self.roles = tuple(type(role) for role in roles)
        self.pass_user = pass_user

    async def __call__(self, event: TelegramObject) -> bool | Dict[str, Any]:
        user = await db.user.get(user_id=event.from_user.id)
        if not user or not isinstance(user.role, self.roles):
            return False
        if self.pass_user:
            return {'user': user}
        return True


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
        super().__init__(UserRole.OPERATOR, UserRole.OWNER)


class ProviderFilter(RoleFilter):
    """Filter by provider"""

    def __init__(self) -> None:
        super().__init__(UserRole.PROVIDER, UserRole.OWNER)


class ManagerFilter(RoleFilter):
    """Filter by manager"""

    def __init__(self) -> None:
        super().__init__(UserRole.MANAGER, UserRole.OWNER)
