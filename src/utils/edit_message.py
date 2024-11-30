import logging
from typing import Any
from aiogram.types import CallbackQuery, Message


logger = logging.getLogger(__name__)


class EditMessage:
    """
    Support class for edit message text
    """
    def __init__(
        self, event: CallbackQuery | Message,
        send_message: bool = False,
    ) -> None:
        self.send_message = send_message
        self.bot = event.bot
        self.default_kwds = {'chat_id': event.from_user.id}

        if isinstance(event, Message):
            self.default_kwds['message_id'] = event.message_id
        elif event.inline_message_id:
            self.default_kwds['inline_message_id'] = event.inline_message_id
        else:
            self.default_kwds['message_id'] = event.message.message_id

    async def __call__(self, **kwds: Any) -> Message:
        if self.send_message:
            return await self.bot.send_message(**kwds, chat_id=self.default_kwds['chat_id'])

        try:
            return await self.bot.edit_message_text(**kwds, **self.default_kwds)

        except Exception as e:
            logger.warning(f'Error when editing message - {e}')
            await self.bot.send_message(**kwds, chat_id=self.default_kwds['chat_id'])
