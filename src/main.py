from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio

from src import database
from src import config
from src.misc.utils import logging_setup, dir_setup


async def on_startup(bot: Bot) -> None:
    # getting info about bot
    await database.setup()
    config.BOT_USERNAME = (await bot.get_me()).username
    # starting bot polling~
    await bot.delete_webhook(drop_pending_updates=True)


def start() -> None:
    "Start bot"
    # setupping
    dir_setup()
    logging_setup()
    # creating instances bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(
        ...
    )
    dp.startup.register(on_startup)
    asyncio.run(dp.start_polling(bot))


if __name__ == '__main__':
    start()
