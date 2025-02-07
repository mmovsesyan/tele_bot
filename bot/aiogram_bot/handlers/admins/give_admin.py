from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.middlewares import include_middlewares, admin_middleware
from bot.aiogram_bot.misc.states import AddAdmin
from bot.database.requests.users import get_user, update_user
from bot.texts import ADM_USER_NOT_FOUND_TXT, ADM_USER_ADDED_TXT, ADM_USER_DELETED_TXT, \
    ADM_WAIT_FOR_UID_TO_GIVE_ADMIN_TXT

router = Router()
include_middlewares(router, admin_middleware)

@router.callback_query(F.data == "add_admin")
async def add_admin(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(ADM_WAIT_FOR_UID_TO_GIVE_ADMIN_TXT, reply_markup=cancel_keyboard)
    await state.set_state(AddAdmin.uid)

@router.message(AddAdmin.uid, F.text)
async def add_admin_2(message: types.Message, state: FSMContext):

    uid = message.text.replace("@", "").replace("https://", "").replace("t.me/", "")
    user = await get_user(uid)
    if not user:
        await message.answer(ADM_USER_NOT_FOUND_TXT.format(uid), reply_markup=cancel_keyboard)
        return
    await state.clear()
    new_status = not user.is_admin
    await update_user(user.user_id, is_admin=new_status)
    text = ADM_USER_ADDED_TXT if new_status else ADM_USER_DELETED_TXT
    await message.answer(text, reply_markup=admin_keyboard)
