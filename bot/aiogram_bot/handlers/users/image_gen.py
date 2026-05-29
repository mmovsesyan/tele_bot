from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot import veoapi, image_ai
from bot.aiogram_bot.markups.user_keyboards import cancel_keyboard, get_main_menu
from bot.aiogram_bot.misc.states import VideoGeneration, ImageGeneration
from bot.database.models import User
from bot.database.requests.users import minus_video, minus_image
from bot.texts import ERROR_TXT, VIDEO_WAIT_PROMT_TXT, VIDEO_NO_GENS_TXT, VIDEO_WAIT_TXT, IMAGE_WAIT_PROMT_TXT, \
    IMAGE_NO_GENS_TXT, IMAGE_WAIT_TXT, USE_PART_TXT
from bot.utils.config import ADMIN_IDS
from bot.utils.util import write_error

router = Router()


@router.callback_query(F.data == "image_generation")
async def image_generation(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.message.answer(IMAGE_WAIT_PROMT_TXT, parse_mode='HTML', reply_markup=cancel_keyboard)
    await state.set_state(ImageGeneration.prompt)


@router.message(ImageGeneration.prompt, F.text)
async def image_generation_2(message: types.Message, state: FSMContext, user: User):
    if user.image_gens < 1:
        if not (user.user_id in ADMIN_IDS or user.is_admin):
            await message.answer(IMAGE_NO_GENS_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))
            return
    prompt = message.text
    await message.answer(IMAGE_WAIT_TXT, parse_mode='HTML', reply_markup=get_main_menu(user))
    await state.clear()
    try:
        if not (user.user_id in ADMIN_IDS or user.is_admin):

            await minus_image(user.user_id)
        image_url = await image_ai.gen_image(prompt)
        await message.reply_photo(image_url)
        await message.answer(
            USE_PART_TXT, parse_mode="HTML", reply_markup=get_main_menu(user)
        )

    except Exception as e:

        filename = write_error(e)
        await message.reply(ERROR_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
