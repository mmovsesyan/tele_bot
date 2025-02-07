import asyncio

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.misc.middlewares import (admin_middleware,
                                              include_middlewares)
from bot.database.requests.users import get_users
from bot.texts import ADM_FILE_WITH_USERS_TXT, ADM_WAIT_TXT
from bot.utils.util import generate_users_xlsx

router = Router()
include_middlewares(router, admin_middleware)


@router.callback_query(F.data == "upload_users")
async def upload_users(call: types.CallbackQuery, state: FSMContext):
    users = await get_users()
    await call.message.answer(ADM_WAIT_TXT, parse_mode='HTML')

    xlsx_file = await asyncio.to_thread(generate_users_xlsx, users)

    await call.message.answer_document(
        document=types.BufferedInputFile(xlsx_file.getvalue(), filename="users.xlsx"),
        caption=ADM_FILE_WITH_USERS_TXT
    )
