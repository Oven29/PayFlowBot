from enum import Enum


class UserRole(str, Enum):
    OWNER = 'OWNER'
    ADMIN = 'ADMIN'
    PROVIDER = 'PROVIDER'
    OPERATOR = 'OPERATOR'
    MANAGER = 'MANAGER'
    IS_FREEZE = 'IS_FREEZE'


class UserProviderStatus(str, Enum):
    NO_PROVIDER = 'NO_PROVIDER'
    INACTIVE = 'INACTIVE'
    ACTIVE_INTER = 'ACTIVE_INTER'
    ACTIVE_TINK = 'ACTIVE_TINK'
    BUSY = 'BUSY'
