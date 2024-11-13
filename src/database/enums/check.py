from enum import Enum


class CheckStatus(str, Enum):
    OK = 'OK'
    UNDERPAYMENT = 'UNDERKPAYMENT'
    OVERPAYMENT = 'OVERPAYMENT'
    ERROR = 'ERROR'
