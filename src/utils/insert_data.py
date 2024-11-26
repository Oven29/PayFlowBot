import asyncio
from datetime import datetime

from src.database.enums import UserRole, UserProviderStatus, OrderBank, OrderStatus, CheckStatus
from src.database.models.user import User
from src.database.models.order import Order, RejectOrder
from src.database.models.check import Check
from src.database.connect import base_config


"""
    Insert data for tests
"""


# Тестовые данные для модели User
test_users = [
    {
        "id": 2,
        "user_id": 101,
        "username": "admin_user",
        "reg_date": datetime(2023, 5, 1),
        "role": UserRole.ADMIN,
        "balance": 5000,
        "commission": 100,
        "provider_status": UserProviderStatus.NO_PROVIDER,
    },
    {
        "id": 3,
        "user_id": 102,
        "username": "provider_user",
        "reg_date": datetime(2023, 6, 15),
        "role": UserRole.PROVIDER,
        "balance": 700,
        "commission": 30,
        "provider_status": UserProviderStatus.ACTIVE_TINK,
    },
    {
        "id": 4,
        "user_id": 103,
        "username": "operator_user",
        "reg_date": datetime(2023, 8, 10),
        "role": UserRole.OPERATOR,
        "balance": 0,
        "commission": 0,
        "provider_status": UserProviderStatus.NO_PROVIDER,
    }
]

# Тестовые данные для модели Order
test_orders = [
    {
        "id": 1,
        "amount": 1200.50,
        "bank": OrderBank.TINK,
        "card": "1234567812345678",
        "created_date": datetime(2023, 8, 15),
        "status": OrderStatus.CREATED,
        "operator": test_users[2],
        "provider": None,
        "cancel_reason": None,
        "dispute_reason": None
    },
    {
        "id": 2,
        "amount": 3400.75,
        "bank": OrderBank.TINK,
        "card": "8765432187654321",
        "created_date": datetime(2023, 8, 18),
        "status": OrderStatus.CANCELLED,
        "operator": test_users[2]['id'],
        "provider": test_users[1]['id'],
        "cancel_reason": "Customer request",
        "dispute_reason": None
    },
    {
        "id": 3,
        "amount": 3400.75,
        "bank": OrderBank.TINK,
        "card": "8765432187654321",
        "created_date": datetime(2023, 8, 18),
        "status": OrderStatus.PROCESSING,
        "operator": test_users[2]['id'],
        "provider": test_users[1]['id'],
        "cancel_reason": None,
        "dispute_reason": None
    }
]

# Тестовые данные для модели Check
test_checks = [
    {
        "id": 1,
        "add_date": datetime(2023, 8, 20),
        "amount": 1000.00,
        "order": test_orders[0]['id'],
        "status": CheckStatus.OK,
        "url": "https://example.com"
    },
    {
        "id": 2,
        "add_date": datetime(2023, 8, 25),
        "amount": 500.00,
        "order": test_orders[1]['id'],
        "status": CheckStatus.OVERPAYMENT,
        "url": "https://example.com"
    }
]


# Тестовые данные для модели RejectOrder
test_reject_orders = [
    {
        "id": 1,
        "date": datetime(2023, 9, 1),
        "order": test_orders[2]['id'],
        "provider": test_users[1],
        "reason": "Insufficient balance"
    }
]


async def insert_data() -> None:
    """Insert test data to database"""
    async with base_config.database:
        for user in test_users:
            await User.objects.create(**user)

        for order in test_orders:
            await Order.objects.create(**order)

        for check in test_checks:
            await Check.objects.create(**check)

        for reject_order in test_reject_orders:
            await RejectOrder.objects.create(**reject_order)


if __name__ == '__main__':
    """
        Run this file to insert test data to database
        Usage: ```
            python -m src.utils.insert_data
        ```
    """
    asyncio.run(insert_data())
