from enum import Enum


class OrderBank(str, Enum):
    TINK = 'TINK'
    INTER = 'INTER'


class OrderStatus(str, Enum):
    CREATED = 'CREATED'  # новые
    CANCELLED = 'CANCELLED'  # отмененные
    COMPLETED = 'COMPLETED'  # выполненные (обработанные)
    DISPUTE = 'DISPUTE'  # диспут
    PROCESSING = 'PROCESSING'  # в работе
