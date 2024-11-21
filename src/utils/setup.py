import os
import logging
from logging.handlers import RotatingFileHandler

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

    logging.getLogger('databases').setLevel(logging.WARNING)

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
