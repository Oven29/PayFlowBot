from enum import Enum


class UserRole(str, Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    PROVIDER = 'provider'
    OPERATOR = 'operator'
    MANAGER = 'manager'
