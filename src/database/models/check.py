from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, ForeignKey, Text, Float
import pydantic

from .order import Order
from ..connect import base_config
from ..enums import CheckStatus, OrderBank


class Check(Model):
    ormar_config = base_config.copy(tablename='orders')
    id: int = Integer(primary_key=True)

    add_date: datetime = DateTime(default=datetime.now)
    amount: float = Float()
    order: Order = ForeignKey(Order, ondelete='CASCADE')
    status: CheckStatus = Enum(enum_class=CheckStatus)

    @pydantic.computed_field()
    def bank(self) -> Optional[OrderBank]:
        try:
            return self.order.bank
        except:
            pass
