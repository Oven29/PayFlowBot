from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import asyncio

from src import database
from src import config
from src.utils.setup import logging_setup, dir_setup
from src.handlers import common, admin, operator, provider


async def on_startup(bot: Bot) -> None:
    # getting info about bot
    await database.setup()
    config.BOT_USERNAME = (await bot.get_me()).username
    
    await bot.set_my_commands([
        BotCommand(command='/start', description='Открыть меню'),
        BotCommand(command='/admin', description='Открыть меню админа'),
        BotCommand(command='/operator', description='Открыть меню оператора'),
        BotCommand(command='/provider', description='Открыть меню провайдера'),
        BotCommand(command='/manager', description='Открыть меню менеджера'),
        BotCommand(command='/freeze', description='Заморозить аккаунт'),
        BotCommand(command='/remove', description='Удалить аккаунт'),
        BotCommand(command='/turn-off', description='Завершить сессию'),
    ])
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
        *common.routers,
        *admin.routers,
        *operator.routers,
        *provider.routers,
    )
    dp.startup.register(on_startup)
    asyncio.run(dp.start_polling(bot))


if __name__ == '__main__':
    start()
