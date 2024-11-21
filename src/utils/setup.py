import os
import logging
from logging.handlers import RotatingFileHandler

from src import config


def dir_setup() -> None:
    "Dir setup"
    if not os.path.exists(config.LOGS_DIR):
        os.mkdir(config.LOGS_DIR)

    if not os.path.exists(config.DATA_DIR):
        os.mkdir(config.DATA_DIR)


def logging_setup() -> None:
    "Logging setup"
    if config.LOGGING_LEVEL is None:
        return

    logging.getLogger('databases').setLevel(logging.WARNING)

    logging.basicConfig(
        handlers=(
            logging.StreamHandler(),
            RotatingFileHandler(
                filename=os.path.join(config.LOGS_DIR, f'.log'),
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
