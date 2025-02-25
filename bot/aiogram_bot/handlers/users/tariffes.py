import time

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from bot import ckassa, json_worker
from bot.aiogram_bot.markups.user_keyboards import (
    generate_plans_kbd,
    get_confirm_kbd,
    get_main_menu,
    cancel_keyboard, generate_video_plans_kbd,
)
from bot.aiogram_bot.misc.states import BuyPlan
from bot.database.models import User
from bot.database.requests.users import update_user
from bot.texts import (
    PLANS_PART_1_TXT,
    TO_BUY_PLAN_GO_LINK_TXT,
    INCORRECT_PAYMENT_TXT,
    ERROR_PAYMENT_TXT,
    PAYMENT_CONFIRMATION_TXT,
    USE_PART_TXT,
    PLANS_PART_2_TXT, VIDEO_PLANS_TXT, VIDEO_PAYMENT_CONFIRMATION_TXT, TO_BUY_VIDEO_GO_LINK_TXT,
)
from bot.utils.config import CKASSA_MAIN_PROPERTY
from bot.utils.json_worker import get_plan_by_name
from bot.utils.util import write_error, format_datetime, convert_to_usd

router = Router()


def get_txt_plans(json_file):
    txt_plans = ""
    for i, plan in enumerate(json_file):
        if plan["price"] == 0:
            continue

        txt_plans += f"{plan['emoji']} <b>Тариф \"{plan['name']}\"</b>\n  - Цена: {plan['price']} RUB / месяц\n  - Запросов в день: GPT {plan['day_reqs']['gpt']} запросов в день | Qwen {plan['day_reqs']['qwen']} запросов в день"
        if i != len(json_file) - 1:
            txt_plans += "\n\n"
    return txt_plans


@router.callback_query(F.data == "show_plans")
async def show_plans(call: types.CallbackQuery, state: FSMContext, user: User):
    """
    Обработчик для вывода тарифов.
    """

    json_file = await json_worker.read("config/plans.json")
    try:
        name = get_plan_by_name(json_file, user.plan)["name"]
    except:
        await update_user(user.user_id, plan="free")
        return
    if user.plan_due_to:
        txt_prev = PLANS_PART_2_TXT.format(
            name,
            user.request_remains["gpt"],
            user.request_remains["qwen"],
            format_datetime(user.plan_due_to),
            user.video_gens,
            get_txt_plans(json_file),
        )
    else:
        txt_prev = PLANS_PART_1_TXT.format(
            name,
            user.request_remains["gpt"],
            user.request_remains["qwen"],
            user.video_gens,
            get_txt_plans(json_file),
        )

    await call.message.edit_text(
        txt_prev, reply_markup=generate_plans_kbd(json_file), parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data and c.data.startswith("plan_"))
@router.callback_query(lambda c: c.data and c.data.startswith("video_plan:"))
async def select_plan(call: types.CallbackQuery, state: FSMContext, user: User):
    if call.data.startswith("plan_"):
        type_ = 'default'
        json_plans = await json_worker.read("config/plans.json")
        plan_uid = call.data.split("_", 1)[1]
        plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
        answer_txt = PAYMENT_CONFIRMATION_TXT.format(plan["name"], plan["price"])

    elif call.data.startswith("video_plan:"):
        type_ = 'video'
        plan_uid = call.data.split(":")[1]
        json_plans = await json_worker.read("config/video_plans.json")
        plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
        answer_txt = VIDEO_PAYMENT_CONFIRMATION_TXT.format(plan["videos"], plan["usd_price"])
    if not plan:
        await call.answer("Неверный тариф")
        return

    await state.set_state(BuyPlan.confirmation)
    await state.update_data(plan_uid=plan_uid, type_=type_)

    await call.message.edit_text(
        answer_txt,
        reply_markup=get_confirm_kbd(plan_uid),
        parse_mode="HTML",
    )


@router.callback_query(
    BuyPlan.confirmation,
    lambda c: c.data and c.data.startswith("confirm_purchase_"),
)
async def confirm_purchase(call: types.CallbackQuery, state: FSMContext, user: User):
    await call.answer("Ожидайте...")
    plan_uid = call.data.split("_", 2)[-1]
    data = await state.get_data()

    if data.get("plan_uid") != plan_uid:
        await call.message.answer(ERROR_PAYMENT_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
    type_ = data.get("type_")
    if type_ == 'default':
        json_plans = await json_worker.read("config/plans.json")
    elif type_ == 'video':
        json_plans = await json_worker.read("config/video_plans.json")

    plan = next((p for p in json_plans if p["uid"] == plan_uid), None)
    if type_ == 'default':
        price = plan['price']
        desc = f"{user.user_id}:{plan['uid']}:30"
    elif type_ == 'video':
        price = await convert_to_usd(plan['usd_price'], 'USD')
        desc = f"v:{user.user_id}:{plan['uid']}"

    if not plan:
        await call.answer(INCORRECT_PAYMENT_TXT, show_alert=True)
        await state.clear()
        return

    try:
        payment_link = await ckassa.create_invoice(
            amount=price,
            properties=[
                {"name": CKASSA_MAIN_PROPERTY, "value": desc},
                {"name": "ID", "value": int(f"{user.user_id}{int(time.time())}")},
                {"name": "telegram_ID", "value": user.user_id},
            ]
        )

        if type_ == 'default':
            answer_txt = TO_BUY_PLAN_GO_LINK_TXT.format(
                plan["emoji"], plan["name"], plan["price"], payment_link
            )
        elif type_ == 'video':
            answer_txt = TO_BUY_VIDEO_GO_LINK_TXT.format(
                plan["videos"], price, payment_link
            )
    except Exception as e:
        write_error(e)
        await call.message.answer(ERROR_PAYMENT_TXT, reply_markup=get_main_menu(user))
        await state.clear()
        return
    await state.clear()

    await call.message.edit_text(
        answer_txt,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

    await call.message.answer(
        USE_PART_TXT, reply_markup=cancel_keyboard, parse_mode="HTML"
    )


@router.callback_query(F.data == "video_buy")
async def video_buy_join(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()

    json_file = await json_worker.read("config/video_plans.json")
    plans = []
    for el in json_file:
        plans.append(f'👉 <b>{el['videos']} видео</b> за {el['usd_price']} USD')
    final_txt = VIDEO_PLANS_TXT + '\n'.join(plans)
    await call.message.answer(final_txt, parse_mode='HTML', reply_markup=generate_video_plans_kbd(json_file))
