import hashlib
from aiogram import Router, F
from aiogram.types import CallbackQuery, \
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from src.database import db
from src.database.enums import UserRole, OrderStatus
from src.keyboards import admin as kb
from src.filters.role import RoleFilter
from src.misc.utils import generate_rand_string


router = Router(name=__name__)
router.message.filter(RoleFilter(UserRole.OWNER, UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.OWNER, UserRole.ADMIN))


@router.callback_query(F.data == 'admin orders')
async def admin_orders_menu(call: CallbackQuery) -> None:
    await call.message.edit_text(
        text='Выберите тип заявки',
        reply_markup=kb.orders_menu,
    )


@router.inline_query(F.query.startswith('order_'))
async def order_inline(query: InlineQuery) -> None:
    try:
        _, status, *search_query = query.query.split()
    except ValueError:
        return

    offset = query.offset or 0
    orders = await db.order.search(
        status=OrderStatus._value2member_map_.get(status, OrderStatus.CREATED),
        search_query=' '.join(search_query),
        offset=offset,
    )

    await query.answer(
        results=[InlineQueryResultArticle(
            id=hashlib.md5(generate_rand_string(8).encode()).hexdigest(),
            input_message_content=InputTextMessageContent(
                message_text=order.message,
            ),
            title=order.title,
            description=order.description,
        ) for order in orders],
        cache_time=30,
        is_personal=True,
        next_offset=offset + 1 if len(orders) >= 49 else None,
    )
