from .user import UserRole, UserProviderStatus
from .token import AccessType
from .order import OrderBank, OrderStatus
from .check import CheckStatus


access_type_to_user_role = {
    AccessType.ADMIN: UserRole.ADMIN,
    AccessType.MANAGER: UserRole.MANAGER,
    AccessType.OPERATOR: UserRole.OPERATOR,
    AccessType.PROVIDER: UserRole.PROVIDER,
}

order_status_to_text = {
    OrderStatus.CREATED: 'Новые заявки',
    OrderStatus.COMPLETED: 'Обработанные',
    OrderStatus.CANCELLED: 'Отменённые',
    OrderStatus.PROCESSING: 'В работе',
    OrderStatus.DISPUTE: 'Диспут',
}

order_bank_to_text = {
    OrderBank.TINK: 'Тинькофф',
    OrderBank.TINK_SBP: 'Тинькофф СБП',
    OrderBank.INTER: 'Межбанк',
}
