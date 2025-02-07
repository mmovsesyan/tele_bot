from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import get_main_menu
from bot.aiogram_bot.misc.middlewares import admin_middleware, include_middlewares
from bot.database.models import User
from bot.texts import ADMIN_JOIN_TXT, ADM_BACKED_TO_MAIN_MENU_TXT

router = Router()
include_middlewares(router, admin_middleware)

@router.callback_query(F.data == "join_admin")
async def join_admin(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(ADMIN_JOIN_TXT, reply_markup=admin_keyboard)

@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.message.edit_text(ADM_BACKED_TO_MAIN_MENU_TXT, reply_markup=get_main_menu(user))
