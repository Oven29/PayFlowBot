from typing import Optional

from .order import get as get_order
from ..connect import base_config
from ..enums import CheckStatus
from ..models.check import Check


async def get_by_order(
    order_id: int,
) -> Optional[Check]:
    """Get check

    Args:
        order_id (int): Order ID

    Returns:
        Check: Check
    """
    async with base_config.database:
        return await Check.objects.get(order__id=order_id)


async def create(
    amount: float,
    status: CheckStatus,
    url: str,
    order: Optional[Check] = None,
    order_id: Optional[int] = None,
) -> Check:
    """Create check

    Args:
        amount (float): Check amount
        status (CheckStatus): Check status
        url (str): Check URL
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
