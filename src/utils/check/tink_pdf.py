import io
import aiohttp
from datetime import datetime
import logging
import re
from pdfminer.high_level import extract_text

from .base import BaseCheck
from .exceptions import *
from src.utils.use_bot import UseBot


logger = logging.getLogger(__name__)


class TinkPdfCheck(BaseCheck):
    async def valid(self) -> None:
        try:
            # Download file
            async with UseBot() as bot:
                bytes_file = io.BytesIO()
                tg_file = await bot.get_file(file_id=self.url)
                await bot.download_file(
                    file_path=tg_file.file_path,
                    destination=bytes_file,
                )

            # Extract text from file
            text = extract_text(bytes_file).strip()

        except Exception as e:
            logger.error(e)
            raise UnknownCheckError

        # Patterns for extracting data
        date_time_pattern = r"(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})"
        card_number_pattern = r"\*(\d+)"
        amount_pattern = r"\b(\d+\s*i)\b"

        # Extraction of date and time
        date_time_match = re.search(date_time_pattern, text)
        if not date_time_match:
            raise CheckNotFound

        # Conversion to datetime
        self.date = datetime.strptime(f"{date_time_match.group(1)} {date_time_match.group(2)}", "%d.%m.%Y %H:%M:%S")
        self.valid_date()

        # Extraction of card number
        card_match = re.search(card_number_pattern, text)
        if not card_match:
            raise CheckNotFound
        self.valid_card(f"*{card_match.group(1)}")

        # Extraction of amount
        amount_match = re.search(amount_pattern, text)
        if not amount_match:
            raise CheckNotFound
        self.amount = float(amount_match.group(1).strip().split(' ', 1)[0])
