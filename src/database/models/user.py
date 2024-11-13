from datetime import datetime
from typing import Optional
from ormar import Integer, Model, String, DateTime, Enum, Float, Boolean
import pydantic

from ..connect import base_config
from ..enums import UserRole, UserProviderStatus, OrderStatus, user_role_to_text


class User(Model):
    ormar_config = base_config.copy(tablename='users')
    id: int = Integer(primary_key=True)

    user_id: int = Integer(unique=True)
    username: Optional[str] = String(nullable=True, max_length=64)
    reg_date: datetime = DateTime(default=datetime.now)
    role: UserRole = Enum(enum_class=UserRole)
    balance: int = Integer(default=0)
    commission: float = Float(default=0)
    provider_status: UserProviderStatus = Enum(enum_class=UserProviderStatus, default=UserProviderStatus.NO_PROVIDER)

    @pydantic.computed_field()
    def title(self) -> str:
        if self.username:
            return f'@{self.username} (id={self.user_id})'
        return str(self.user_id)

    @pydantic.computed_field()
    def description(self) -> str:
        res = f'Роль: {user_role_to_text[self.role]} Дата регитсрации: {self.reg_date}'
        if self.role in (UserRole.OPERATOR, UserRole.PROVIDER):
            res += f' Баланс: {self.balance} Комиссия: {self.commission}'
        return res

    @pydantic.computed_field()
    def message(self) -> str:
        res = f'<b>Пользователь {self.title}</b>\n\n' \
            f'<b>Дата регистрации:</b> <code>{self.reg_date}</code>'

        if self.role in (UserRole.OPERATOR, UserRole.PROVIDER, UserRole.MANAGER):
            res += f'\n<b>Комиссия:</b> {self.commission}\n' \
                f'<b>Текущий баланс:</b> {self.balance}'

        orders = getattr(self, f'{self.role.value}_orders', None)
        if not orders:
            return res
        completed_orders = [el for el in orders if el.status is OrderStatus.COMPLETED]
        canceled_orders = [el for el in orders if el.status is OrderStatus.CANCELLED]

        return f'{res}\n' \
            f'<b>Кол-во обработанных заявок:</b> {len(completed_orders)}\n' \
            f'<b>Кол-во отменённых заявок:</b> {len(canceled_orders)}\n' \
            f'<b>Общий объём обработанных денег:</b> {sum(el.amount for el in completed_orders)}'

    def calculate_balance(self, order_amount: int) -> int:
        return self.balance + order_amount * (self.percent / 100)
