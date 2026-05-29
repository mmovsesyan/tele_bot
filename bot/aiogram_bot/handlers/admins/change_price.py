from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from bot import json_worker
from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.media_worker import downloading
from bot.aiogram_bot.misc.middlewares import include_middlewares, admin_middleware
from bot.aiogram_bot.misc.states import ChangePlans
from bot.texts import ADM_SEND_NEW_PRICES_TXT, ADM_CURRENT_PRICES_TXT, ADM_JSON_ERROR_TXT, ADM_UPDATED_SUCCESS_TXT

router = Router()
include_middlewares(router, admin_middleware)



@router.callback_query(F.data == "change_prices")
async def change_prices(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer_document(FSInputFile('config/plans.json'), caption=ADM_CURRENT_PRICES_TXT)
    await call.message.answer(ADM_SEND_NEW_PRICES_TXT, reply_markup=cancel_keyboard)
    await state.set_state(ChangePlans.new_plans)


@router.message(ChangePlans.new_plans, F.document)
async def change_prices_2(message: types.Message, state: FSMContext):
    filename_path = await downloading(message, None)
    filename_path = filename_path[0]
    status = await json_worker.validate(filename_path)
    if not status:
        await message.answer(ADM_JSON_ERROR_TXT, reply_markup=cancel_keyboard)
        return
    await state.clear()
    await json_worker.write(filename_path, 'config/plans.json')
    await message.answer(ADM_UPDATED_SUCCESS_TXT, reply_markup=admin_keyboard)
