from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, ForeignKey, Text, Float
import pydantic

from .order import Order
from ..connect import base_config
from ..enums import CheckStatus, CheckType, OrderBank


class Check(Model):
    ormar_config = base_config.copy(tablename='checks')
    id: int = Integer(primary_key=True)

    add_date: datetime = DateTime(default=datetime.now)
    amount: float = Float()
    order: Order = ForeignKey(Order, ondelete='CASCADE')
    status: CheckStatus = Enum(enum_class=CheckStatus)
    url: str = String(max_length=512, nullable=False)
    type: CheckType = Enum(enum_class=CheckType, nullable=True)

    @pydantic.computed_field()
    def bank(self) -> Optional[OrderBank]:
        if self.bank:
            return self.order.bank
