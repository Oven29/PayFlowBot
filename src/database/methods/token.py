from typing import Optional

from ..connect import base_config
from ..enums import AccessType
from ..models.token import IndividualToken


async def create(
    access_type: AccessType,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
) -> IndividualToken:
    """Create token

    Args:
        access_type (UserRole): User role
        user_id (Optional[int]): User Telegram ID. Defaults to None.
        username (Optional[str], optional): Username. Defaults to None.

    Returns:
        IndividualToken: Created token
    """
    async with base_config.database:
        return await IndividualToken.objects.create(
            access_type=access_type,
            user_id=user_id,
            username=username,
        )


async def get_by_code(code: str) -> Optional[IndividualToken]:
    """Get token by code

    Args:
        code (str): Token code

    Returns:
        Optional[IndividualToken]: Token
    """
    async with base_config.database:
        return await IndividualToken.objects.get_or_none(code=code)
