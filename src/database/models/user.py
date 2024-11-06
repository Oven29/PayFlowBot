from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum

from ..connect import base_config
from ..enums import UserRole, UserProviderStatus


class User(Model):
    ormar_config = base_config.copy(tablename='users')
    id: int = Integer(primary_key=True)

    user_id: int = Integer(unique=True)
    username: Optional[str] = String(nullable=True, max_length=64)
    reg_date: datetime = DateTime(default=datetime.now)
    role: UserRole = Enum(enum_class=UserRole)
    balance: int = Integer(default=0)
    commission: int = Integer(default=0)
    provider_status: UserProviderStatus = Enum(enum_class=UserProviderStatus, default=UserProviderStatus.NO_PROVIDER)
