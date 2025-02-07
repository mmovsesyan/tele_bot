import json
from typing import List

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.serialization import deserialize_telegram_object_to_python

from bot.aiogram_bot.markups.admin_keyboards import mass_mail_keyboard, admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.media_worker import copy_post
from bot.aiogram_bot.misc.middlewares import include_middlewares, admin_middleware
from bot.aiogram_bot.misc.states import MassSend
from bot.database.models import User
from bot.database.requests.users import get_users
from bot.texts import ADMIN_WAIT_FOR_POST_TXT, ADMIN_CHECK_POST_TXT, ADMIN_START_MAILING_TXT, \
    ADMIN_MAILING_COMPLETED_TXT, USE_PART_TXT

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "mass_send")
async def mass_send_1(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(ADMIN_WAIT_FOR_POST_TXT, reply_markup=cancel_keyboard)
    await state.set_state(MassSend.msg)


@router.message(MassSend.msg)
async def send_users_2(message: types.Message, state: FSMContext, user: User, album: List[types.Message] = None):
    await copy_post(album or message, user.user_id, message.bot)
    await message.answer(ADMIN_CHECK_POST_TXT, reply_markup=mass_mail_keyboard)

    json_album = [json.dumps(deserialize_telegram_object_to_python(m)) for m in album] if album else None
    json_msg = json.dumps(deserialize_telegram_object_to_python(message))
    await state.update_data(json_album=json_album, json_msg=json_msg)
    await state.set_state(MassSend.confirmation)


@router.callback_query(MassSend.confirmation, F.data == 'ok')
async def send_users_3(call: types.CallbackQuery, state: FSMContext):
    users = await get_users()
    data = await state.get_data()
    await state.clear()
    waitmsg = await call.message.answer(ADMIN_START_MAILING_TXT.format(len(users)))
    await call.message.answer(text=USE_PART_TXT, reply_markup=admin_keyboard, parse_mode='HTML')

    album = [Message.model_validate(json.loads(m)) for m in data.get("json_album")] if data.get("json_album") else None
    msg = Message.model_validate(json.loads(data.get("json_msg"))) if data.get("json_msg") else None

    for user_ in users:
        try:
            await copy_post(album or msg, user_.user_id, call.bot)
        except Exception as e:
            continue
    await waitmsg.reply(ADMIN_MAILING_COMPLETED_TXT)
