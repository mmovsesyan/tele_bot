from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.user_keyboards import get_settings_kbd
from bot.database.models import User
from bot.database.requests.users import update_user, get_model
from bot.texts import SETTINGS_TXT

router = Router()


@router.callback_query(F.data == "show_settings")
async def show_settings(call: types.CallbackQuery, state: FSMContext, user: User):
    model = get_model(user).name
    await call.message.edit_text(SETTINGS_TXT.format(model), parse_mode='HTML', reply_markup=get_settings_kbd(user))

@router.callback_query(F.data.startswith("change_model_to:"))
async def change_model_to(call: types.CallbackQuery, state: FSMContext, user: User):
    new_model = call.data.split(":")[1]
    if user.current_model == new_model:
        ...
    else:
        await update_user(user.user_id, current_model=new_model)
        user.current_model = new_model
        model = get_model(user).name

        await call.message.edit_text(SETTINGS_TXT.format(model), parse_mode='HTML', reply_markup=get_settings_kbd(user))
