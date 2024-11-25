from datetime import datetime, timedelta
import logging
import random
from aiogram.enums import ParseMode

from src import config
from src.database import db
from src.database.enums import UserProviderStatus, OrderStatus, order_bank_to_provider_status
from src.keyboards import provider as kb
from src.utils.scheduler import scheduler, DateTrigger
from src.utils.use_bot import UseBot


logger = logging.getLogger(__name__)


async def reject_order(
    order: db.order.Order,
    provider: db.user.User,
) -> None:
    """If provider does not accept order after notify, reject it"""
    logger.info(f'Reject order: {order.id=} {provider.user_id=}')

    await db.order.reject(
        order=order,
        provider=provider,
        reason='Провайдер не принял заявку, автоматическая отмена',
    )
    await db.user.update(
        user=provider,
        provider_status=UserProviderStatus.INACTIVE,
    )
    await distribute_order(order)

    async with UseBot(parse_mode=ParseMode.HTML) as bot:
        await bot.send_message(
            chat_id=provider.user_id,
            text=f'Вы не приняли заявку <b>{order.title}</b>',
        )
        await bot.send_message(
            chat_id=config.REJECT_ORDER_CHAT_ID,
            text=f'Провайдер {provider.title} не принял заявку <b>{order.title}</b> и был отключен.'
                'Заявка передана другому провайдеру',
        )


async def notify_provider(
    order: db.order.Order,
    provider: db.user.User,
) -> None:
    """Notify provider about current order, if his does not accept it"""
    logger.info(f'Notify provider: {order.id=} {provider.user_id=}')

    scheduler.add_job(
        name=f'reject_order {provider.user_id}',
        func=reject_order,
        trigger=DateTrigger(datetime.now() + timedelta(minutes=3)),
        kwargs={
            'order': order,
            'provider': provider,
        },
    )

    async with UseBot(parse_mode=ParseMode.HTML) as bot:
        await bot.send_message(
            chat_id=provider.user_id,
            text=f'У Вас новая заявка <b>{order.title}</b>',
            reply_markup=kb.accept_order(order.id),        
        )


async def distribute(
    order: db.order.Order,
    provider: db.user.User,
) -> None:
    """Distribute order to provider"""
    logger.info(f'Distribute order: {order.id=} to {provider.user_id=}')

    await db.user.update(
        user=provider,
        provider_status=UserProviderStatus.BUSY,
    )
    await db.order.update(
        order=order,
        status=OrderStatus.PROCESSING,
    )

    scheduler.add_job(
        name=f'notify_provider {provider.user_id}',
        func=notify_provider,
        trigger=DateTrigger(datetime.now() + timedelta(minutes=5)),
        kwargs={
            'order': order,
            'provider': provider,
        },
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
    rejects = await db.order.get_reject_orders(order)

    free_providers = await db.user.select(
        provider_status=order_bank_to_provider_status[order.bank],
        user_id__not_in=[el.provider.user_id for el in rejects],
    )
    if not len(free_providers):
        return

    provider = random.choice(free_providers)
    await distribute(order, provider)


async def go_on_shift(
    provider: db.user.User,
) -> None:
    """Find free order for provider if exists"""
    order = await db.order.get_current(provider_id=provider.user_id)
    if not order is None:
        async with UseBot(parse_mode=ParseMode.HTML) as bot:
            await bot.send_message(
                text=f'Текущая заявка\n\n{order.get_message(provider.role)}',
                reply_markup=kb.finish_order(order.id),
            )
        return

    rejects = await db.order.get_reject_orders(order)

    free_orders = await db.order.select(
        status=OrderStatus.CREATED,
        id__not_in=[el.order.id for el in rejects],
    )
    if not len(free_orders):
        return

    order = free_orders[0]
    await distribute(order, provider)
