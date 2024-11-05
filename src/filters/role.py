from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

from ..database.enums import UserRole
from ..database.models import users


class RoleFilter(BaseFilter):
    """Filter by role"""

    def __init__(self, role: UserRole) -> None:
        self.role = role

    async def __call__(self, event: TelegramObject) -> bool:
        user = await users.get_or_none(user_id=event.from_user.id)
        return user and user.role == self.role.value
