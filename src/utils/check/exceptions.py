class BaseCheckException(Exception):
    """Base check exception"""


class InvalidCheckUrl(BaseCheckException):
    """Invalid check URL"""
    message = 'Некорректный ввод ссылки, вид ссылки https://link.tbank.ru/123AbcD456'


class CheckNotFound(BaseCheckException):
    """Check not found"""
    message = 'Чек не найдена'


class InvalidCheckCard(BaseCheckException):
    """Invalid check card"""
    message = 'Некорректные реквизиты'


class InvalidCheckRecipient(BaseCheckException):
    """Invalid check recepient"""
    message = 'Некорректные данные получателя'


class InvalidCheckDate(BaseCheckException):
    """Invalid check date"""
    message = 'Некорректное время пополнения'


class UnknownCheckError(BaseCheckException):
    """Unknown error"""
    message = 'Неизвестная ошибка'
