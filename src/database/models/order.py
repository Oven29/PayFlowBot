from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, ForeignKey, Text, Float

from .user import User
from ..connect import base_config
from ..enums import OrderBank, OrderStatus


class Order(Model):
    ormar_config = base_config.copy(tablename='orders')
    id: int = Integer(primary_key=True)

    amount: float = Float()
    bank: OrderBank = Enum(enum_class=OrderBank)
    card: str = String(max_length=16)
    created_date: datetime = DateTime(default=datetime.now)
    status: OrderStatus = Enum(enum_class=OrderStatus, default=OrderStatus.CREATED)
    operator: User = ForeignKey(User, ondelete='CASCADE', related_name='operator_orders')
    provider: Optional[User] = ForeignKey(User, nullable=True, ondelete='CASCADE', related_name='provider_orders')
    cancel_reason: Optional[str] = Text(nullable=True)
    dispute_reason: Optional[str] = Text(nullable=True)


class RejectOrder(Model):
    ormar_config = base_config.copy(tablename='reject_orders')
    id: int = Integer(primary_key=True)

    date: datetime = DateTime(default=datetime.now)
    order: Order = ForeignKey(Order, ondelete='CASCADE')
    provider: User = ForeignKey(User, ondelete='CASCADE')
    reason: str = Text()
