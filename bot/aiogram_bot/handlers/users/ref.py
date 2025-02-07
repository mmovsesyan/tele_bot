import html

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot.aiogram_bot.markups.user_keyboards import get_main_menu
from bot.database.models import User
from bot.database.requests.users import get_users_count_invited_by
from bot.texts import REF_INFO_TXT

router = Router()


def get_ref_link(user_id: int):
    from bot.utils import config
    return f"https://t.me/{config.BOT_USERNAME}?start=r{user_id}"

@router.callback_query(F.data == "show_ref")
async def ref_(call: types.CallbackQuery, state: FSMContext, user: User):
    link = get_ref_link(user.user_id)
    count = await get_users_count_invited_by(user.user_id)
    await call.message.edit_text(REF_INFO_TXT.format(html.escape(link), count, user.invited_this_month), parse_mode='HTML', reply_markup=get_main_menu(user))