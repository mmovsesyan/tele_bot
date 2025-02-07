from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.user_keyboards import get_main_menu
from bot.database.models import User
from bot.texts import INFO_TXT
router = Router()

@router.callback_query(F.data == "show_info")
async def show_info(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.message.edit_text(INFO_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))