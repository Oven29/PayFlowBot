from enum import Enum


class OrderBank(str, Enum):
    TINK = 'tink'
    TINK_SBP = 'tink_sbp'
    INTER = 'inter'


class OrderStatus(str, Enum):
    CREATED = 'created'  # новые
    CANCELLED = 'cancelled'  # отмененные
    COMPLETED = 'completed'  # выполненные (обработанные)
    DISPUTE = 'dispute'  # диспут
    PROCESSING = 'processing'  # в работе
