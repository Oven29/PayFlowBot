from abc import ABC, abstractmethod


class BaseCheck(ABC):
    def __init__(
        self,
        url: str,
        card: str,
    ) -> None:
        self.url = url
        self.card = card
        self.amount = 0

    @abstractmethod
    async def valid(self) -> bool:
        """Check if check is valid"""
        raise NotImplementedError
