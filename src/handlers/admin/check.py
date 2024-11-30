import logging
from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery

from src import config
from src.database import db
from src.database.enums import CheckStatus, OrderStatus
from src.keyboards import common as kb
from src.utils.edit_message import EditMessage


router = Router(name=__name__)
router.message.filter(F.chat.id == config.CHECK_CHAT_ID)
router.callback_query.filter(F.message.chat.id == config.CHECK_CHAT_ID)

logger = logging.getLogger(__name__)


async def notify_and_edit_message(call: CallbackQuery, text: str) -> None:
    await call.answer(
        text=text,
        show_alert=True,
    )
    await EditMessage(call)(
        text=f'{call.message.text}\n\n{text}',
    )


@router.callback_query(F.data.startswith('accept-check'))
async def accept_check(call: CallbackQuery, bot: Bot) -> None:
    _, check_id = call.data.split()
    check = await db.check.get_by_id(check_id=check_id)

    if not check.order.status in OrderStatus.PROCESSING:
        return await notify_and_edit_message(call, 'Заказ уже выполнен')

    await notify_and_edit_message(call, '✅ Чек принят')
    await bot.send_message(
        chat_id=check.order.provider.user_id,
        text=f'Чек <b>{check.amount}</b> принят администрацией\nНажмите на кнопку, чтобы сохранить его',
        reply_markup=kb.save_check(check.id)
    )


@router.callback_query(F.data.startswith('reject-check'))
async def reject_check(call: CallbackQuery, bot: Bot) -> None:
    _, check_id = call.data.split()
    check = await db.check.get_by_id(check_id=check_id)

    await db.check.update(
        check_id=check.id,
        status=CheckStatus.REJECT,
    )

    await notify_and_edit_message(call, f'❌ Чек отклонён')
    await bot.send_message(
        chat_id=check.order.provider.user_id,
        text=f'Чек <b>{check.amount}</b> отклонён',
    )
