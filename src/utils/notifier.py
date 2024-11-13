import logging
from aiogram import Bot

from src.database import db
from src.database.enums.user import UserRole


logger = logging.getLogger(__name__)


async def admin_notify(text: str, bot: Bot) -> None:
    """Send message to all admins"""
    admins = await db.user.select(
        role__in=(UserRole.ADMIN, UserRole.OWNER),
    )
    for admin in admins:
        try:
            await bot.send_message(
                chat_id=admin.user_id,
                text=text,
            )
        except Exception as e:
            logger.warning(e)
