from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.middlewares import (admin_middleware,
                                              include_middlewares)
from bot.aiogram_bot.misc.states import BanUser
from bot.database.requests.users import get_user, update_user
from bot.texts import (ADM_SEND_UID_TO_BAN_TXT, ADM_USER_BLOCKED_TXT,
                       ADM_USER_NOT_FOUND_TXT, ADM_USER_UNBLOCKED_TXT)

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "ban_user")
async def ban_user(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(ADM_SEND_UID_TO_BAN_TXT, reply_markup=cancel_keyboard)
    await state.set_state(BanUser.uid)


@router.message(BanUser.uid, F.text)
async def ban_user_2(message: types.Message, state: FSMContext):
    uid = message.text.replace("@", "").replace("https://", "").replace("t.me/", "")
    user = await get_user(uid)
    if not user:
        await message.answer(ADM_USER_NOT_FOUND_TXT.format(uid), reply_markup=cancel_keyboard)
        return
    await state.clear()
    new_status = not user.is_blocked
    await update_user(user.user_id, is_blocked=new_status)
    text = ADM_USER_BLOCKED_TXT if new_status else ADM_USER_UNBLOCKED_TXT
    await message.answer(text, reply_markup=admin_keyboard)
