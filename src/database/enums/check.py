from enum import Enum


class CheckStatus(str, Enum):
    OK = 'ok'
    UNDERKPAYMENT = 'underpay'
    OVERPAYMENT = 'overpay'
    ERROR = 'error'
