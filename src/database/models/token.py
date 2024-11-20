from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, ForeignKey
import pydantic

from .user import User
from ..connect import base_config
from ..enums import AccessType
from src.utils.other import generate_rand_string
from src import config


class IndividualToken(Model):
    ormar_config = base_config.copy(tablename='individual_tokens')
    id: int = Integer(primary_key=True)

    code: str = String(max_length=16, default=lambda: generate_rand_string(16))
    created_date: datetime = DateTime(default=datetime.now)
    activate_date: Optional[datetime] = DateTime(nullable=True)
    user: Optional[User] = ForeignKey(User, nullable=True, ondelete='CASCADE')
    username: Optional[str] = String(max_length=64, nullable=True)
    user_id: Optional[int] = Integer(nullable=True)
    access_type: AccessType = Enum(enum_class=AccessType)
    manager: Optional[User] = ForeignKey(User, nullable=True, ondelete='CASCADE', related_name='manager')

    @pydantic.computed_field()
    def link(self) -> str:
        return f'https://t.me/{config.BOT_USERNAME}?start={self.code}'

    def check_available(self, user_id: int, username: str | None) -> bool:
        "Check if token is available for user"
        return self.user is None and \
              (self.user_id is None or self.user_id == user_id) and \
              (self.username is None or self.username == username)
