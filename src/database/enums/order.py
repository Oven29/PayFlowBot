from enum import Enum


class OrderBank(str, Enum):
    TINK = 'TINK'
    TINK_SBP = 'TINK_SBP'
    INTER = 'INTER'


class OrderStatus(str, Enum):
    CREATED = 'CREATED'  # новые
    CANCELLED = 'CANCELLED'  # отмененные
    COMPLETED = 'COMPLETED'  # выполненные (обработанные)
    DISPUTE = 'DISPUTE'  # диспут
    PROCESSING = 'PROCESSING'  # в работе
