import random
from aiogram.enums import ParseMode

from src.database import db
from src.database.enums import UserProviderStatus, OrderStatus, order_bank_to_provider_status
from src.keyboards import provider as kb
from src.utils.use_bot import UseBot


async def distribute(
    order: db.order.Order,
    provider: db.user.User,
) -> None:
    """Distribute order to provider"""
    await db.user.update(
        user=provider,
        provider_status=UserProviderStatus.BUSY,
    )
    await db.order.update(
        order=order,
        status=OrderStatus.PROCESSING,
    )

    async with UseBot(parse_mode=ParseMode.HTML) as bot:
        await bot.send_message(
            chat_id=provider.user_id,
            text=f'Новая заявка <b>{order.title}</b>',
            reply_markup=kb.accept_order(order.id),
        )


async def distribute_order(
    order: db.order.Order,
) -> None:
    """Distribute order to provider if exists free providers"""
    free_providers = await db.user.select(
        provider_status__in=order_bank_to_provider_status(order.bank),
    )
    if not len(free_providers):
        return

    provider = random.choice(free_providers)
    await distribute(order, provider)


async def go_on_shift(
    provider: db.user.User,
) -> None:
    """Find free order for provider if exists"""
    free_orders = await db.order.select(
        status=OrderStatus.CREATED,
    )
    if not len(free_orders):
        return

    order = free_orders[0]
    await distribute(order, provider)
