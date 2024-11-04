from __future__ import annotations
from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum

from ..connect import base_config
from ..enums import UserRole


class User(Model):
    ormar_config = base_config.copy(tablename='users')
    id: int = Integer(primary_key=True)

    user_id: int = Integer(unique=True)
    username: Optional[str] = String(nullable=True, max_length=64)
    reg_date: datetime = DateTime(default=datetime.now)
    role: str = Enum(enum_class=UserRole)
