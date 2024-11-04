from enum import Enum


class UserRole(str, Enum):
    ADMIN = 'admin'
    PROVIDER = 'provider'
    OPERATOR = 'operator'
