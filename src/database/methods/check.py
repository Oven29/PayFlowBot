from datetime import datetime
from typing import Any, List, Optional

from .order import get as get_order
from ..connect import base_config
from ..enums import CheckStatus, CheckType
from ..models.check import Check


async def get_by_order(
    order_id: int,
) -> List[Check]:
    """Get order`s checks

    Args:
        order_id (int): Order ID

    Returns:
        List[Check]: List of checks
    """
    async with base_config.database:
        return await Check.objects.filter(order__id=order_id).all()


async def create(
    amount: float,
    status: CheckStatus,
    url: str,
    date: datetime,
    type: Optional[CheckType] = None,
    order: Optional[Check] = None,
    order_id: Optional[int] = None,
) -> Check:
    """Create check

    Args:
        amount (float): Check amount
        status (CheckStatus): Check status
        url (str): Check URL
        date (datetime): Check date
        type (Optional[CheckType], optional): Check type. Defaults to None.
        order (Optional[Check], optional): Check. Defaults to None.
        order_id (Optional[int], optional): Order ID. Defaults to None.

    Returns:
        Check: Created check
    """
    async with base_config.database:
        if order is None:
            order = await get_order(order_id)

        return await Check.objects.create(
            amount=amount,
            url=url,
            type=type,
            add_date=date,
            order=order,
            status=status,
        )


async def check_exists_by_url(
    url: str,
) -> bool:
    """Check if check exists by URL

    Args:
        url (str): Check URL

    Returns:
        bool: Check exists
    """
    async with base_config.database:
        return await Check.objects.filter(url=url).exists()


async def get_by_id(
    check_id: int,
) -> Optional[Check]:
    """Get check by ID

    Args:
        check_id (int): Check ID

    Returns:
        Optional[Check]: Check
    """
    async with base_config.database:
        return await Check.objects.select_related([
            Check.order, Check.order.provider,
        ]).filter(id=check_id).first()


async def update(
    check_id: int,
    **kwargs: Any,
) -> None:
    """Update check status

    Args:
        check_id (int): Check ID
        **kwargs (Any): Fields to update
    """
    async with base_config.database:
        await Check.objects.select_related([
            Check.order, Check.order.provider,
        ]).filter(id=check_id).update(**kwargs)


async def delete(
    check_id: int,
) -> None:
    """Delete check

    Args:
        check_id (int): Check ID
    """
    async with base_config.database:
        await Check.objects.filter(id=check_id).delete()
