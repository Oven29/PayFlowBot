from typing import Any
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from src import config


class UseBot:
    """
    Async context manager for aiogram.Bot instance.
    """
    async def __aenter__(self, **kwargs: Any) -> Bot:
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
