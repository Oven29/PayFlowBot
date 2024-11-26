import logging
from typing import Any, List, Optional

from . import user
from ..connect import base_config
from ..enums import OrderStatus, OrderBank
from ..models.order import Order, RejectOrder
from ..models.user import User


logger = logging.getLogger(__name__)


async def get(
    order_id: int,
) -> Optional[Order]:
    """Get order

    Args:
        order_id (int): Order ID

    Returns:
        Optional[Order]: Order
    """
    logger.info(f'Get order: {order_id}')
    async with base_config.database:
        result = await Order.objects.select_related([
            'operator', 'provider',
        ]).filter(id=order_id).limit(1).all()
    
        return result[0] if len(result) else None


async def create(
    uid: str,
    amount: float,
    bank: OrderBank,
    card: str,
    operator: Optional[User] = None,
    operator_id: Optional[int] = None,
) -> Order:
    """Create order

    Args:
        uid (str): Order UID
        amount (float): Order amount
        bank (OrderBank): Order bank
        card (str): Card number
        operator (Optional[User], optional): Operator. Defaults to None.
        operator_id (Optional[int], optional): Operator Telegram ID. Defaults to None.

    Returns:
        Order: Created order
    """
    if operator is None:
        operator = await user.get(user_id=operator_id)

    logger.info(f'Create order: {uid=} {amount=} {bank=} {card=} {operator.id=}')
    async with base_config.database:
        return await Order.objects.create(
            uid=uid,
            amount=amount,
            bank=bank,
            card=card,
            operator=operator,
        )


async def update(
    order: Optional[Order] = None,
    order_id: Optional[int] = None,
    **kwargs: Any,
) -> Order:
    """Update order

    Args:
        order (Optional[Order], optional): Order. Defaults to None.
        order_id (Optional[int], optional): Order ID. Defaults to None.
        **kwargs (Any): Fields to update

    Returns:
        Order: Updated order
    """
    if order is None:
            order = await get(order_id=order_id)

    logger.info(f'Update order: {order.id=} ({kwargs})')
    async with base_config.database:        
        await order.update(**kwargs)

    return order


async def reject(
    provider: User,
    reason: str,
    order: Optional[Order] = None,
    order_id: Optional[int] = None,
) -> Order:
    """Reject order

    Args:
        order (Optional[Order], optional): Order. Defaults to None.
        order_id (Optional[int], optional): Order ID. Defaults to None.
        reason (str): Reject reason

    Returns:
        Order: Updated order
    """    
    if order is None:
        order = await get(order_id=order_id)

    logger.info(f'Reject order: {order.id=} {provider.id=} {reason=}')
    async with base_config.database:
        await RejectOrder.objects.create(
            order=order,
            provider=provider,
            reason=reason,
        )
        await order.update(status=OrderStatus.CREATED)

    return order


async def search(
    status: OrderStatus | None,
    search_query: str,
    offset: int = 0,
    **kwargs: Any,
) -> List[Order]:
    """Search orders

    Args:
        status (OrderStatus | None): Order status
        search_query (str): Search query
        offset (int, optional): Offset. Defaults to 0.
        **kwargs (Any): Additional params for search

    Returns:
        List[Order]: List of orders
    """
    async with base_config.database:
        filter_kwargs = kwargs.copy()
        if not status is None:
            filter_kwargs['status'] = status
        if search_query.strip():
            filter_kwargs['card__contains'] = filter_kwargs['uid__contains'] = filter_kwargs['operator__username__contains'] =\
                filter_kwargs['provider__username__contains'] = filter_kwargs['id__contains'] = search_query

        return await Order.objects.select_related([
            'provider', 'operator', 'checks',
        ]).filter(**filter_kwargs).offset(offset * 50).limit(50).all()


async def delete(
    order_id: int,
) -> None:
    """Delete order

    Args:
        order_id (int): Order ID
    """
    logger.info(f'Delete order: {order_id}')
    async with base_config.database:
        await Order.objects.filter(id=order_id).delete()


async def get_user_orders(
    opearator_id: Optional[int] = None,
    provider_id: Optional[int] = None,
) -> List[Order]:
    """Get operator orders

    Args:
        opearator_id (Optional[int], optional): Operator Telegram ID. Defaults to None.
        provider_id (Optional[int], optional): Provider Telegram ID. Defaults to None.

    Returns:
        List[Order]: List of orders
    """
    filter_kwargs = {}
    if opearator_id:
        filter_kwargs['operator__user_id'] = opearator_id
    if provider_id:
        filter_kwargs['provider__user_id'] = provider_id

    logger.info(f'Get user orders: {filter_kwargs}')
    async with base_config.database:
        return await Order.objects.select_related([
            Order.operator, Order.provider, 'checks',
        ]).filter(**filter_kwargs).all()


async def select(
    **kwargs: Any,
) -> List[Order]:
    """Select orders

    Args:
        **kwargs (Any): Filter params

    Returns:
        List[Order]: List of orders
    """
    logger.info(f'Select orders: {kwargs}')
    async with base_config.database:
        return await Order.objects.select_related([
            Order.operator, Order.provider, 'checks',
        ]).filter(**kwargs).all()


async def get_current(
    operator_id: Optional[int] = None,
    provider_id: Optional[int] = None,
) -> Optional[Order]:
    """Get current order

    Args:
        operator_id (Optional[int]): Operator Telegram ID. Default None.
        provider_id (Optional[int]): Provider Telegram ID. Default None.

    Returns:
        Optional[Order]: Order
    """
    filters = {'status': OrderStatus.PROCESSING}
    if operator_id:
        filters['operator__user_id'] = operator_id
    if provider_id:
        filters['provider__user_id'] = provider_id

    logger.info(f'Get current order: {operator_id=} {provider_id=}')
    async with base_config.database:
        return await Order.objects.select_related([
            Order.operator, Order.provider, 'checks',
        ]).filter(**filters).get_or_none()


async def get_reject_orders(
    order: Optional[Order] = None,
    provider: Optional[User] = None,
) -> List[RejectOrder]:
    """Get reject users

    Args:
        order (Optional[Order], optional): Order. Defaults to None.
        provider (Optional[User], optional): Provider. Defaults to None.

    Returns:
        List[RejectOrder]: List of element RejectUsers
    """
    filters = {}
    if not order is None:
        filters['order'] = order
    if not provider is None:
        filters['provider'] = provider

    logger.info(f'Get reject orders: {filters}')
    async with base_config.database:
        return await RejectOrder.objects.select_related([
            RejectOrder.order, RejectOrder.provider,
        ]).filter(**filters).all()
