from enum import Enum


class CheckStatus(str, Enum):
    WAIT = 'WAIT'
    REJECT = 'REJECT'
    OK = 'OK'
    UNDERPAYMENT = 'UNDERKPAYMENT'
    OVERPAYMENT = 'OVERPAYMENT'
    ERROR = 'ERROR'


class CheckType(str, Enum):
    PDF = 'PDF'
    URL = 'URL'
