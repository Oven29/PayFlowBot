import logging
import dotenv
import os
import pathlib
from typing import Final, Optional


ROOT_DIR: Final[str] = pathlib.Path(__file__).parents[1]
dotenv.load_dotenv(
    dotenv_path=os.path.join(ROOT_DIR, '.env'),
    override=True,
    encoding='utf-8',
)

DATA_DIR: Final[str] = os.path.join(ROOT_DIR, 'data')
LOGS_DIR: Final[str] = os.path.join(ROOT_DIR, 'logs')

BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN')
OWNER_ID: Final[str] = int(os.getenv('OWNER_ID') or 0)

LOGGING_LEVEL: Final[str] = logging._nameToLevel.get(os.getenv('LOGGING', 'INFO').upper(), logging.INFO)

BOT_USERNAME: Optional[str] = ...

DATABASE_URL: Final[str] = os.getenv('DATABASE_URL', f'sqlite:///' + os.path.join(DATA_DIR, 'database.db'))
REDIS_URL: Final[str] = os.getenv('REDIS_URL')

OVERPAYEMNT_CHAT_ID: Final[int] = os.getenv('OVERPAYEMNT_CHAT_ID', -1)
ORDER_CHAT_ID: Final[int] = os.getenv('ORDER_CHAT_ID', -1)
REJECT_ORDER_CHAT_ID: Final[int] = os.getenv('REJECT_ORDER_CHAT_ID', -1)
