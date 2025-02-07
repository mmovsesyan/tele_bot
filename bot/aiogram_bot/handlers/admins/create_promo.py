from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.admin_keyboards import admin_keyboard
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard
from bot.aiogram_bot.misc.middlewares import include_middlewares, admin_middleware
from bot.aiogram_bot.misc.states import CreatePromo
from bot.database.requests.promocodes import add_promocode, get_promocode_by_name
from bot.texts import ADM_SEND_ME_PROMO_TXT, ADM_PROMO_CREATED_TXT, ADM_PROMO_EXISTS_TXT

router = Router()
include_middlewares(router, admin_middleware)

@router.callback_query(F.data == "create_promocode")
async def create_promo(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(ADM_SEND_ME_PROMO_TXT, reply_markup=cancel_keyboard)
    await state.set_state(CreatePromo.promo)


@router.message(CreatePromo.promo, F.text)
async def create_promo_2(message: types.Message, state: FSMContext):
    promo = message.text
    if await get_promocode_by_name(promo):
        await message.answer(ADM_PROMO_EXISTS_TXT.format(promo), reply_markup=admin_keyboard)
        await state.clear()
        return
    await add_promocode(value=promo)
    await state.clear()
    await message.answer(ADM_PROMO_CREATED_TXT.format(promo), reply_markup=admin_keyboard)

