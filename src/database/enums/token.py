from enum import Enum


class AccessType(str, Enum):
    ADMIN = 'admin'
    PROVIDER = 'provider'
    OPERATOR = 'operator'
    MANAGER = 'manager'
