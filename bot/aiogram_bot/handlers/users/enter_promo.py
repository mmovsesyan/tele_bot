from datetime import datetime, timedelta

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard, get_main_menu
from bot.aiogram_bot.misc.states import EnterPromo
from bot.database.models import User
from bot.database.requests.promocodes import get_promocode_by_name
from bot.database.requests.promocodesactivations import add_promocodeactivation, get_promocode_activation_by_user_id
from bot.texts import US_SEND_ME_PROMO_TXT, US_PROMO_ACTIVATED, US_ALREADY_PROMO_ACTIVATED, US_PROMO_INVALID_TXT, \
    USE_PART_TXT, US_ALREADY_HAVE_PLAN
from bot.utils.plans_worker import give_plan

router = Router()

@router.callback_query(F.data == "enter_promo")
async def enter_promo(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(US_SEND_ME_PROMO_TXT, reply_markup=cancel_keyboard)
    await state.set_state(EnterPromo.promo)


@router.message(EnterPromo.promo,F.text)
async def enter_promo_2(message: types.Message, state: FSMContext, user: User):
    promo = message.text

    promo_db = await get_promocode_by_name(promo)
    await state.clear()
    if user.plan != 'free':
        await message.answer(US_ALREADY_HAVE_PLAN,reply_markup=get_main_menu(user))
        return
    if promo_db:
        if not await get_promocode_activation_by_user_id(user.user_id, promo_db.id):
            await add_promocodeactivation(user_id=user.user_id, promo_id=promo_db.id)
            await give_plan(user.user_id, 'trial', (datetime.now() + timedelta(days=7)).strftime('%d.%m.%Y'))
            await message.answer(US_PROMO_ACTIVATED)
        else:
            await message.answer(US_ALREADY_PROMO_ACTIVATED)
    else:
        await message.answer(US_PROMO_INVALID_TXT)

    await message.answer(text=USE_PART_TXT, reply_markup=get_main_menu(user), parse_mode='HTML')
