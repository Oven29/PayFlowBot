from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, ForeignKey, Text, Float
import pydantic

from .user import User
from ..connect import base_config
from ..enums import UserRole, OrderBank, OrderStatus, order_status_to_text, order_bank_to_text


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

    @pydantic.computed_field()
    def title(self) -> str:
        return f'№{self.id} {order_status_to_text[self.status]} {self.amount}'

    @pydantic.computed_field()
    def description(self) -> str:
        res = f'{order_bank_to_text[self.bank]} на {self.amount} "{self.card}" от {self.created_date} '
        if self.provider and self.operator:
            res += f'провайдер - {self.provider.title} оператор - {self.operator.title}'
        return res

    def get_message(self, role: UserRole) -> str:
        res = f'Заявка №<i>{self.id}</i> от {self.created_date}\n\n' \
            f'<b>Сумма:</b> <code>{self.amount}</code>\n' \
            f'<b>Номер карты:</b> {self.card}\n' \
            f'<b>Банк:</b> {order_bank_to_text[self.bank]}\n' \
            f'<b>Статус:</b> {order_status_to_text[self.status]}\n'
        if self.operator and not role is UserRole.OPERATOR:
            res += f'<b>Оператор:</b> {self.operator.title}\n'
        if self.provider and not role is UserRole.PROVIDER:
            res += f'<b>Провайдер:</b> {self.provider.title}\n'
        if self.checks:
            res += '\n\n<b>Чеки:</b>\n' + '\n'.join(f'<code>{el.amount}</code> - {el.url}' for el in self.checks)
        if self.cancel_reason:
            res += f'\n\n<b>Причина отмены:</b> <i>{self.cancel_reason}</i>'
        if self.dispute_reason:
            res += f'\n\n<b>Причина диспута:</b> <i>{self.dispute_reason}</i>'
        return res


class RejectOrder(Model):
    ormar_config = base_config.copy(tablename='reject_orders')
    id: int = Integer(primary_key=True)

    date: datetime = DateTime(default=datetime.now)
    order: Order = ForeignKey(Order, ondelete='CASCADE')
    provider: User = ForeignKey(User, ondelete='CASCADE')
    reason: str = Text()
