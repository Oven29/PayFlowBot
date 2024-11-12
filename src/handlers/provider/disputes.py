from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.database import db
from src.database.enums import UserProviderStatus
from src.keyboards import provider as kb
from src.utils.edit_message import EditMessage
from src.filters.role import ProviderFilter


router = Router(name=__name__)
router.message.filter(ProviderFilter())
router.callback_query.filter(ProviderFilter())
