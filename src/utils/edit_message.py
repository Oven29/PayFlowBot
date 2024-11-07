from typing import Any
from aiogram.types import CallbackQuery, Message

from src import config


class EditMessage:
    """
    Support class for edit message text
    """
    def __init__(self, event: CallbackQuery | Message) -> None:
        self.message = event if isinstance(event, Message) else event.message

    async def __call__(self, *args: Any, **kwds: Any) -> Message:
        if self.message.from_user.username != config.BOT_USERNAME:
            return await self.message.answer(*args, **kwds)

        if self.message.text:
            return await self.message.edit_text(*args, **kwds)

        return await self.message.edit_caption(*args, **kwds)
