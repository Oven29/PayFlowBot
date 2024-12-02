from abc import ABC, abstractmethod
from datetime import datetime
from fnmatch import fnmatch
from typing import Any

from .exceptions import InvalidCheckDate, InvalidCheckCard
from src.database import db


class BaseCheck(ABC):
    def __init__(
        self,
        url: str,
        order: db.order.Order,
        **kwargs: Any,
    ) -> None:
        self.url = url
        self.card = order.card
        self.created_date = order.created_date
        self.date = kwargs.get('date')
        self.amount = kwargs.get('amount', 0)

    def valid_card(self, card: str) -> None:
        """Check if check card is valid, raise exception if not"""
        # if not fnmatch(self.card, card):
        #     raise InvalidCheckCard

    def valid_date(self) -> None:
        """Check if check date is valid, raise exception if not"""
        # if self.date is None or not self.created_date < self.date < datetime.now():
        #     raise InvalidCheckDate

    @abstractmethod
    async def valid(self) -> bool:
        """Check if check is valid"""
        raise NotImplementedError
