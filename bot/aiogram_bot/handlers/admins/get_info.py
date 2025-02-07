from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.middlewares import (admin_middleware,
                                              include_middlewares)
from bot.aiogram_bot.misc.states import GetInfo
from bot.database.models import User
from bot.database.requests.users import get_user
from bot.texts import (ADM_USER_NOT_FOUND_TXT,
                       ADM_WAIT_FOR_UID_TO_GET_INFO_TXT, USE_PART_TXT,
                       USER_INFO_TXT)
from bot.utils.config import ADMIN_IDS
from bot.utils.util import format_datetime

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "get_info")
async def get_info(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        ADM_WAIT_FOR_UID_TO_GET_INFO_TXT, reply_markup=cancel_keyboard
    )
    await state.set_state(GetInfo.uid)


@router.message(GetInfo.uid, F.text)
async def get_info_2(message: types.Message, state: FSMContext, user: User):
    uid = message.text.replace("@", "").replace("https://", "").replace("t.me/", "")
    user = await get_user(uid)
    if not user:
        await message.answer(
            ADM_USER_NOT_FOUND_TXT.format(uid), reply_markup=cancel_keyboard
        )
        return
    await state.clear()
    await message.answer(
        USER_INFO_TXT.format(
            user.id,
            user.user_id,
            user.username if user.username else "Не указан",
            user.full_name,
            user.plan,
            format_datetime(user.plan_due_to),
            user.invited_by if user.invited_by else "Нет",
            user.invited_this_month,
            "Включена" if user.auto_payment else "Отключена",
            user.current_model,
            "Да" if user.is_blocked else "Нет",
            "Да" if (user.is_admin or user.user_id in ADMIN_IDS) else "Нет",
        ),
        parse_mode="HTML",
    )
    await message.answer(
        text=USE_PART_TXT, reply_markup=admin_keyboard, parse_mode="HTML"
    )
