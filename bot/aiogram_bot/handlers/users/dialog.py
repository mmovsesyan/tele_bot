import html
import os
import uuid

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from bot import AI, json_worker
from bot.aiogram_bot.markups.user_keyboards import (get_main_menu,
                                                    stop_dialog_keyboard)
from bot.aiogram_bot.misc.states import Dialog
from bot.database.models import User
from bot.database.requests.users import update_user
from bot.texts import (AUTO_MODEL_CHANGED_TXT, DIALOG_ENDED_TXT,
                       DIALOG_STARTED_TXT, NO_REQUESTS_FOR_MODEL_TXT,
                       NO_REQUESTS_TXT, PLANS_BTN, START_MSG_FROM_AI_TXT,
                       STOP_DIALOG_BTN, USE_PART_TXT, ERROR_TXT)
from bot.utils.config import ADMIN_IDS, OPENAI_ADMIN_MODEL, OPENAI_ADMIN_TOKEN_LIMIT, OPENAI_MODEL, QWEN_MODEL, \
    ANTHROPIC_MODEL
from bot.utils.json_worker import get_plan_by_name
from bot.utils.util import write_error, escape_markdown_v2

router = Router()


async def auto_change_model(user: User, bot: Bot, type_: int):
    plans = await json_worker.read("config/plans.json")
    plan = get_plan_by_name(plans, user.plan)
    if user.user_id in ADMIN_IDS or user.is_admin:
        return plan

    ai = AI[user.current_model]
    reqs = user.request_remains[user.current_model]
    if reqs <= 0:
        if type_ == 1:
            txt = NO_REQUESTS_TXT.format(ai.name)
        elif type_ == 2:
            txt = NO_REQUESTS_FOR_MODEL_TXT.format(PLANS_BTN)
        await bot.send_message(
            user.user_id,
            txt,
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        if user.current_model in ["gpt", 'claude'] and user.request_remains["qwen"] > 0:
            await update_user(user.user_id, current_model="qwen")
            user.current_model = "qwen"
            ai = AI[user.current_model]
            await bot.send_message(
                user.user_id, AUTO_MODEL_CHANGED_TXT.format(ai.name), parse_mode="HTML"
            )
        else:
            await bot.send_message(
                user.user_id,
                USE_PART_TXT,
                parse_mode="HTML",
                reply_markup=get_main_menu(user),
            )

            return
    return plan


@router.callback_query(F.data == "start_dialog")
async def start_dialog(call: types.CallbackQuery, state: FSMContext, user: User):
    a = await auto_change_model(user, call.bot, type_=2)
    if a:
        await call.message.answer(
            DIALOG_STARTED_TXT, reply_markup=stop_dialog_keyboard, parse_mode="HTML"
        )
        await call.message.answer(START_MSG_FROM_AI_TXT)
        await state.set_state(Dialog.message)


@router.message(F.text == STOP_DIALOG_BTN)
async def stop_dialog(message: types.Message, state: FSMContext, user: User):
    await state.clear()

    await message.answer(
        DIALOG_ENDED_TXT, parse_mode="HTML", reply_markup=types.ReplyKeyboardRemove()
    )
    await message.answer(
        USE_PART_TXT, parse_mode="HTML", reply_markup=get_main_menu(user)
    )


@router.message(Dialog.message, F.text | F.photo | F.voice)
async def dialog(message: types.Message, state: FSMContext, user: User):
    plan = await auto_change_model(user, message.bot, type_=1)
    if not plan:
        await state.clear()
        return
    try:
        ai = AI[user.current_model]

        if user.current_model == 'gpt':
            model = OPENAI_MODEL
        elif user.current_model == 'qwen':
            model = QWEN_MODEL
        elif user.current_model == 'claude':
            model = ANTHROPIC_MODEL
        else:
            return
        if (user.user_id in ADMIN_IDS or user.is_admin) and user.current_model == "gpt":
            model = OPENAI_ADMIN_MODEL
        max_tokens = plan["output_tokens"]
        photo_path = None
        fpath = 'temp'
        os.makedirs(fpath, exist_ok=True)
        if message.photo:
            photo_path = os.path.abspath(os.path.join(fpath, uuid.uuid4().hex + '.jpg'))
            await message.bot.download(message.photo[-1].file_id, photo_path)
            request = message.caption or ''
        elif message.voice:
            voice_path = os.path.abspath(os.path.join(fpath, uuid.uuid4().hex + '.ogg'))
            await message.bot.download(message.voice.file_id, voice_path)
            temp_ai = AI['gpt']
            request = await temp_ai.get_text(voice_path)
            await message.reply(f"🎤 <i>{html.escape(request)}</i>", parse_mode="HTML")

        else:
            request = message.text
        data = await state.get_data()
        messages = data.get("messages", [])
        max_tokens = max_tokens if len(messages) == 0 else int((max_tokens * ((len(messages) / 2) + 1)))
        if user.user_id in ADMIN_IDS or user.is_admin:
            max_tokens = OPENAI_ADMIN_TOKEN_LIMIT
        await message.bot.send_chat_action(message.chat.id, "typing")
        answer, messages = await ai.generate(model, request, messages, max_tokens, photo_path)
        await message.answer(f"```\n{escape_markdown_v2(answer)}\n```", reply_markup=stop_dialog_keyboard,
                             parse_mode=ParseMode.MARKDOWN_V2)
        if user.user_id not in ADMIN_IDS and not user.is_admin:
            user.request_remains[user.current_model] -= 1

        await update_user(user.user_id, request_remains=user.request_remains)
        await state.update_data(messages=messages)
    except Exception as e:
        filename = write_error(e)
        await message.answer(ERROR_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
