from enum import Enum


class UserRole(str, Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    PROVIDER = 'provider'
    OPERATOR = 'operator'
    MANAGER = 'manager'


class UserProviderStatus(str, Enum):
    NO_PROVIDER = '-'
    INACTIVE = 'inactive'
    ACTIVE_INTER = 'inter'
    ACTIVE_TINK = 'tink'
