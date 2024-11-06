from typing import Any, Dict, Optional

from . import user
from ..connect import base_config
from ..enums import OrderStatus, OrderBank
from ..models.order import Order, RejectOrder
from ..models.user import User


async def get(
    order_id: int,
) -> Order:
    """Get order

    Args:
        order_id (int): Order ID

    Returns:
        Order: Order
    """
    async with base_config.database:
        return await Order.objects.get(id=order_id)


async def create(
    amount: float,
    bank: OrderBank,
    card: str,
    operator: Optional[User] = None,
    operator_id: Optional[int] = None,
) -> Order:
    """Create order

    Args:
        amount (float): Order amount
        bank (OrderBank): Order bank
        card (str): Card number
        operator (Optional[User], optional): Operator. Defaults to None.
        operator_id (Optional[int], optional): Operator Telegram ID. Defaults to None.

    Returns:
        Order: Created order
    """
    if operator is None:
        operator = await user.get_or_none(operator_id)

    async with base_config.database:
        return await Order.objects.create(
            amount=amount,
            bank=bank,
            card=card,
            operator=operator,
        )


async def update(
    order: Optional[Order] = None,
    order_id: Optional[int] = None,
    **kwargs: Dict[str, Any],
) -> None:
    """Update order

    Args:
        order (Optional[Order], optional): Order. Defaults to None.
        order_id (Optional[int], optional): Order ID. Defaults to None.
        **kwargs (Dict[str, Any]): Fields to update
    """
    async with base_config.database:
        if order is None:
            order = await get(id=order_id)

        await order.update(**kwargs)


async def reject(
    provider: User,
    reason: str,
    order: Optional[Order] = None,
    order_id: Optional[int] = None,
) -> None:
    """Reject order

    Args:
        order (Optional[Order], optional): Order. Defaults to None.
        order_id (Optional[int], optional): Order ID. Defaults to None.
        reason (str): Reject reason
    """
    async with base_config.database:
        if order is None:
            order = await get(id=order_id)

        await RejectOrder.objects.create(
            order=order,
            provider=provider,
            reason=reason,
        )
