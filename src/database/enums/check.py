from enum import Enum


class CheckStatus(str, Enum):
    OK = 'OK'
    UNDERKPAYMENT = 'UNDERKPAYMENT'
    OVERPAYMENT = 'OVERPAYMENT'
    ERROR = 'ERROR'
