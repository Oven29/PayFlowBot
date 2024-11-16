import logging
import dotenv
import os
import pathlib
from typing import Final, Optional


root_dir: Final[str] = pathlib.Path(__file__).parents[1]
dotenv.load_dotenv(
    dotenv_path=os.path.join(root_dir, '.env'),
    override=True,
    encoding='utf-8',
)

data_dir: Final[str] = os.path.join(root_dir, 'data')
logs_dir: Final[str] = os.path.join(root_dir, 'logs')

BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN')
OWNER_ID: Final[str] = int(os.getenv('OWNER_ID') or 0)

LOGGING_LEVEL: Final[str] = logging._nameToLevel.get(os.getenv('LOGGING', 'WARN').upper(), logging.WARN)

BOT_USERNAME: Optional[str] = ...

DATABASE_URL: Final[str] = f'sqlite:///' + os.path.join(data_dir, 'database.db')

OVERPAYEMNT_CHAT_ID: Final[int] = os.getenv('OVERPAYEMNT_CHAT_ID', -1)
ORDER_CHAT_ID: Final[int] = os.getenv('ORDER_CHAT_ID', -1)
