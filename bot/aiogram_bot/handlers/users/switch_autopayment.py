from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.database.models import User
from bot.database.requests.users import update_user
from bot.texts import AUTOPAY_SWITCHED_TXT, AUTOPAY_PART_1_TXT, AUTOPAY_PART_2_TXT

router = Router()

@router.callback_query(F.data == "switch_autopay")
async def switch_autopayment(call: types.CallbackQuery, state: FSMContext, user: User):
    ns = True if user.auto_payment is False else False
    await update_user(user.user_id, auto_payment=ns)
    txt = AUTOPAY_PART_1_TXT if ns else AUTOPAY_PART_2_TXT
    await call.message.answer(AUTOPAY_SWITCHED_TXT.format(txt), parse_mode='HTML')