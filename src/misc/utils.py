import os
import logging
from logging.handlers import RotatingFileHandler
import random
from string import hexdigits
from typing import Any, Dict

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.client.default import DefaultBotProperties

from src import config


def dir_setup() -> None:
    "Dir setup"
    if not os.path.exists(config.logs_dir):
        os.mkdir(config.logs_dir)

    if not os.path.exists(config.data_dir):
        os.mkdir(config.data_dir)


def logging_setup() -> None:
    "Logging setup"
    if config.LOGGING_LEVEL is None:
        return
    logging.basicConfig(
        handlers=(
            logging.StreamHandler(),
            RotatingFileHandler(
                filename=os.path.join(config.logs_dir, f'.log'),
                mode='w',
                maxBytes=1024 * 1024,
                backupCount=4,
                encoding='utf-8',
            ),
        ),
        format='[%(asctime)s | %(levelname)s | %(name)s]: %(message)s',
        datefmt='%m.%d.%Y %H:%M:%S',
        level=config.LOGGING_LEVEL,
    )


def generate_rand_string(length: int) -> str:
    "Generate random string"
    return ''.join(random.choice(hexdigits) for _ in range(length))
    

class UseBot:
    """
    Async context manager for aiogram.Bot instance.
    """
    async def __aenter__(self, **kwargs: Dict[str, Any]) -> Bot:
        """
        Create Bot instance.
        """
        self._instance = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(**kwargs),
        )
        return self._instance

    async def __aexit__(self, *_) -> None:
        """
        Close Bot instance.
        """
        await self._instance.close()


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
