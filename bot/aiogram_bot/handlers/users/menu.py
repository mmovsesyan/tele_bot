from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.user_keyboards import get_main_menu
from bot.database.models import User
from bot.texts import START_TEXT, CANCELLED_TXT, USE_PART_TXT, REF_TO_INVITED_TXT

router = Router()


@router.message(F.text.startswith("/start"))
async def start_btn(message: types.Message, state: FSMContext, user: User, first_meeting: bool = False):
    await state.clear()
    await message.answer(text=START_TEXT, reply_markup=get_main_menu(user), parse_mode='HTML')
    if first_meeting:
        await message.bot.send_message(message.from_user.id, text=REF_TO_INVITED_TXT, parse_mode='HTML')


@router.callback_query(F.data == "main_menu")
async def back_main_menu(call: types.CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await call.message.edit_text(text=USE_PART_TXT, reply_markup=get_main_menu(user), parse_mode='HTML')

@router.callback_query(F.data == "cancel")
async def back_main_menu(call: types.CallbackQuery, state: FSMContext, user: User):
    await state.clear()
    await call.message.edit_text(text=CANCELLED_TXT, parse_mode='HTML')
    await call.message.answer(USE_PART_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))
