from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot import veoapi
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard, get_main_menu
from bot.aiogram_bot.misc.states import VideoGeneration
from bot.database.models import User
from bot.database.requests.users import minus_video
from bot.texts import ERROR_TXT, VIDEO_WAIT_PROMT_TXT, VIDEO_NO_GENS_TXT, VIDEO_WAIT_TXT
from bot.utils.util import write_error

router = Router()


@router.callback_query(F.data == "video_generation")
async def video_generation(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.message.answer(VIDEO_WAIT_PROMT_TXT, parse_mode='HTML', reply_markup=cancel_keyboard)
    await state.set_state(VideoGeneration.prompt)


@router.message(VideoGeneration.prompt, F.text)
async def video_generation_2(message: types.Message, state: FSMContext, user: User):
    if user.video_gens < 1:
        await message.answer(VIDEO_NO_GENS_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))
        return
    prompt = message.text
    await message.answer(VIDEO_WAIT_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))
    await state.clear()
    try:
        await minus_video(user.user_id)
        result_url = await veoapi.run(prompt)
        await message.reply_video(result_url)
    except Exception as e:

        filename = write_error(e)
        await message.reply(ERROR_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
