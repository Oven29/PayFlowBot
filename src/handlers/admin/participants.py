from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database import db
from src.database.enums import UserRole
from src.keyboards import admin as kb
from src.filters.role import RoleFilter


router = Router(name=__name__)
router.message.filter(RoleFilter(UserRole.OWNER, UserRole.ADMIN))
router.callback_query.filter(RoleFilter(UserRole.OWNER, UserRole.ADMIN))
