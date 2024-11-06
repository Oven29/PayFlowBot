from typing import Tuple
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from src.database.enums import UserRole
from src.database.models import user


class RoleFilter(BaseFilter):
    """Filter by role"""

    def __init__(self, *roles: Tuple[UserRole]) -> None:
        self.roles = roles

    async def __call__(self, event: TelegramObject) -> bool:
        user = await user.get_or_none(user_id=event.from_user.id)
        return user and isinstance(user.role, self.roles)
