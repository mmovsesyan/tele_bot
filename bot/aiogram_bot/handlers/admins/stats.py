from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.misc.middlewares import include_middlewares, admin_middleware
from bot.database.requests.users import get_users
from bot.texts import STATS_TEMPLATE_TXT

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "show_stats")
async def show_stats(call: types.CallbackQuery, state: FSMContext):
    all_users = await get_users()
    len_all_users = len(all_users)
    len_user_with_paid_sub = len([u for u in all_users if u.plan not in ['free', 'trial']])
    await call.message.edit_text(STATS_TEMPLATE_TXT.format(len_all_users, len_user_with_paid_sub), parse_mode='HTML', reply_markup=admin_keyboard)