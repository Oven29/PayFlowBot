from typing import Any, Dict, List, Optional, Tuple

from ..connect import base_config
from ..enums import UserRole
from ..models.user import User


async def get_or_create(
    user_id: int,
    role: UserRole,
    username: Optional[str] = None,
) -> Tuple[User, bool]:
    """Get or create user

    Args:
        user_id (int): User Telegram ID
        role (UserRole): User role
        username (Optional[str], optional): Username. Defaults to None.

    Returns:
        Tuple[bool, User]: Created, User
    """
    async with base_config.database:
        user, created = await User.objects.get_or_create(
            user_id=user_id,
            _defaults={
                'username': username,
                'role': role,
            },
        )

    return user, created


async def get(
    user_id: Optional[int] = None,
    user_pk: Optional[int] = None,
) -> Optional[User]:
    """Get or none user

    Args:
        user_id (Optional[int]): User Telegram ID. Defaults to None.
        user_pk (Optional[int], optional): User ID. Defaults to None.

    Returns:
        Optional[User]: User
    """
    if user_id:
        filters = {'user_id': user_id}
    else:
        filters = {'id': user_pk}

    async with base_config.database:
        return await User.objects.get_or_none(**filters)


async def search(
    role: UserRole | None,
    search_query: str,
    offset: int = 0,
) -> List[User]:
    """Search orders

    Args:
        role (UserRole | None): User role
        search_query (str): Search query
        offset (int, optional): Offset. Defaults to 0.

    Returns:
        List[Order]: List of orders
    """
    async with base_config.database:
        filter_kwargs = {}
        if not role is None:
            filter_kwargs['role'] = role
        if search_query.strip():
            filter_kwargs['id__contains'] = filter_kwargs['user_id__contains'] = filter_kwargs['role__contains'] =\
                filter_kwargs['username__contains'] = search_query

        return await User.objects.select_related([
            'operator_orders', 'provider_orders',
        ]).filter(**filter_kwargs).offset(offset * 50).limit(50).all()


async def delete(
    user_id: Optional[int] = None,
    user_pk: Optional[int] = None,
) -> None:
    """Delete user

    Args:
        user_id (Optional[int]): User Telegram ID. Defaults to None.
        user_pk (Optional[int], optional): User ID. Defaults to None.
    """
    if user_id:
        filters = {'user_id': user_id}
    else:
        filters = {'id': user_pk}

    async with base_config.database:
        await User.objects.filter(**filters).delete()


async def update(
    user_id: Optional[int] = None,
    user_pk: Optional[int] = None,
    user: Optional[User] = None,
    **kwargs: Dict[str, Any],
) -> User:
    """Update user

    Args:
        user_id (Optional[int]): User Telegram ID. Defaults to None.
        user_pk (Optional[int], optional): User ID. Defaults to None.

    Returns:
        User: Updated user
    """
    async with base_config.database:
        if user is None:
            user = await get(user_id=user_id, user_pk=user_pk)
        await user.update(**kwargs)
    
    return user


async def select(
    **kwargs: Any,
) -> List[User]:
    """Select users

    Args:
        **kwargs (Any): Filter params

    Returns:
        List[User]: List of users
    """
    async with base_config.database:
        return await User.objects.select_related([
            'operator_orders', 'provider_orders',
        ]).filter(**kwargs).all()
