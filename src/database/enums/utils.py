from .user import UserRole, UserProviderStatus
from .token import AccessType
from .order import OrderBank, OrderStatus
from .check import CheckStatus


def access_type_to_user_role(access_type: AccessType) -> UserRole:
    """Convert access type to user role"""
    if access_type == AccessType.ADMIN:
        return UserRole.ADMIN
    elif access_type == AccessType.MANAGER:
        return UserRole.MANAGER
    elif access_type == AccessType.OPERATOR:
        return UserRole.OPERATOR
    elif access_type == AccessType.PROVIDER:
        return UserRole.PROVIDER
