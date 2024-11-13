from typing import Any
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from src import config


class UseBot:
    """
    Async context manager for aiogram.Bot instance.
    """
    def __init__(self, **params: Any) -> None:
        self.params = params

    async def __aenter__(self) -> Bot:
        """
        Create Bot instance.
        """
        self._instance = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(**self.params),
        )
        return self._instance

    async def __aexit__(self, *_) -> None:
        """
        Close Bot instance.
        """
        await self._instance.session.close()
