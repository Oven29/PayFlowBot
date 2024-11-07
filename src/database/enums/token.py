from enum import Enum


class AccessType(str, Enum):
    ADMIN = 'ADMIN'
    PROVIDER = 'PROVIDER'
    OPERATOR = 'OPERATOR'
    MANAGER = 'MANAGER'
