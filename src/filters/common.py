import re
from typing import Dict
from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.types import Message


class AmountFilter(BaseFilter):
    "Regexp filter for integer or float"
    pattern = r'^(\d+(\.\d+)?|\d+(,\d+)?|(\.\d+)|(\,\d+))$'

    def __init__(self, pass_value: bool = False) -> None:
        self.pass_value = pass_value

    async def __call__(self, message: Message) -> bool | Dict[str, int | float]:
        text = message.text or message.caption or ''
        if re.match(self.pattern, text) is None:
            return False
        if self.pass_value:
            return {'value': float(text.replace(',', '.'))}
        return True


card_filter = F.text.regexp(r'^\+?[0-9 ]{5,19}$')
